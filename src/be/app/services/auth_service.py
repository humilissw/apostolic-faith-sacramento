"""
Authentication service for handling user authentication operations.
Contains business logic for password recovery and reset.
"""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PasswordResetToken, User, validate_password_complexity
from app.repositories.user_repo import UserRepository
from app.utils import generate_reset_password_email, send_email


class AuthService:
    """
    Service for authentication-related operations.
    Handles business logic for password recovery and reset.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the auth service with a user repository.

        Args:
            user_repository: UserRepository instance for database operations
        """
        self.user_repo = user_repository

    async def initiate_password_recovery(self, email: str, session: AsyncSession) -> None:
        """
        Initiate password recovery by generating a server-side reset token and sending email.

        Security measures:
        - Returns the same message whether the user exists or not (prevents enumeration)
        - Tokens are cryptographically secure random strings stored server-side
        - Each token is single-use and expires after EMAIL_RESET_TOKEN_EXPIRE_HOURS
        - Existing valid tokens for the same user are invalidated before creating a new one

        Args:
            email: Email address of the user requesting password recovery
            session: Database session for token storage
        """
        user = await self.user_repo.get_by_email(email=email)

        if not user:
            # Don't reveal if user exists for security reasons
            return

        # Invalidate any existing valid tokens for this user
        # This prevents token accumulation and ensures only the latest link works
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,  # type: ignore[arg-type]
            PasswordResetToken.invalidated.is_(False),  # type: ignore[attr-defined, arg-type]
            PasswordResetToken.expires_at > datetime.now(timezone.utc),  # type: ignore[arg-type]
        )
        result = await session.execute(stmt)
        existing_tokens = result.scalars().all()
        for token_record in existing_tokens:
            token_record.invalidated = True
        if existing_tokens:
            await session.commit()

        # Generate a cryptographically secure random token (not JWT-based)
        reset_token = secrets.token_urlsafe(32)

        # Calculate expiry
        from app.config import settings

        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
        )

        # Store the token server-side for single-use enforcement
        db_token = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at,
        )
        session.add(db_token)
        await session.commit()

        # Generate email content with the stored token
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=reset_token
        )

        # Send reset password email
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    async def reset_password(self, token: str, new_password: str, session: AsyncSession) -> dict:
        """
        Reset a user's password using a valid single-use reset token.

        Security measures:
        - Token is looked up server-side and verified (not just decoded from JWT)
        - Token must not be expired or invalidated (single-use enforcement)
        - After successful use, the token is invalidated to prevent replay
        - Password complexity is enforced before processing
        - All existing reset tokens for the user are invalidated after a successful reset

        Args:
            token: Password reset token from email link
            new_password: New password to set
            session: Database session for token verification and user lookup

        Raises:
            HTTPException: If token is invalid, expired, or already used
        """
        # Validate new password complexity before processing (fail fast)
        if not validate_password_complexity(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Password must be at least 8 characters "
                    "and contain uppercase, lowercase, digit, "
                    "and special character."
                ),
            )

        # Look up the token server-side (not just decode a JWT)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token == token,  # type: ignore[arg-type]
            PasswordResetToken.invalidated.is_(False),  # type: ignore[attr-defined, arg-type]
        )
        result = await session.execute(stmt)
        stored_token = result.scalar_one_or_none()

        if stored_token is None:
            # Use a generic message to prevent enumeration
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token. Please request a new one.",
            )

        # Check if the token has expired
        expires = stored_token.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            # Mark expired tokens as invalidated for cleanup
            stored_token.invalidated = True
            await session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token. Please request a new one.",
            )

        # Get the user by ID (stored_token.user_id is the user's ID, not email)
        user = await session.get(User, stored_token.user_id)  # type: ignore[arg-type]
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        # Update the password through the repository
        await self.user_repo.update_password(db_user=user, new_password=new_password)

        # Invalidate this token (single-use enforcement)
        stored_token.invalidated = True
        await session.commit()

        # Invalidate ALL other reset tokens for this user (in case they were intercepted)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,  # type: ignore[arg-type]
            PasswordResetToken.invalidated.is_(False),  # type: ignore[attr-defined]
        )
        result = await session.execute(stmt)
        other_tokens = result.scalars().all()
        for other_token in other_tokens:
            other_token.invalidated = True
        if other_tokens:
            await session.commit()

        return {"message": "Password updated successfully"}

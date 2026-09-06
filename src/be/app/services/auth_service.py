"""
Authentication service for handling user authentication operations.
Contains business logic for password recovery and reset.
"""

import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.reset_tokens import sign_reset_token, verify_reset_token_link
from app.models import PasswordResetToken, User, validate_password_complexity
from app.repositories.user_repo import UserRepository
from app.utils import (
    generate_new_account_email,
    generate_reset_password_email,
    send_email,
)


class AuthService:
    """
    Service for authentication-related operations.
    Handles business logic for password recovery and reset.
    """

    def __init__(self, user_repository: UserRepository, session: AsyncSession):
        """
        Initialize the auth service with a user repository and database session.

        Args:
            user_repository: UserRepository instance for database operations
            session: Database session used for token storage/verification
        """
        self.user_repo = user_repository
        self.session = session

    async def initiate_password_recovery(self, email: str) -> None:
        """Initiate password recovery by generating a server-side reset token and sending email.

        This is a thin wrapper around the bulk path so single and bulk requests
        share exactly one implementation. A delivery failure for a single
        address is swallowed (the response must not reveal whether the account
        exists); bulk callers inspect the per-email results themselves.

        Args:
            email: Email address of the user requesting password recovery
        """
        await self.initiate_password_recovery_bulk([email], raise_if_all_fail=False)

    async def initiate_password_recovery_bulk(
        self, emails: list[str], raise_if_all_fail: bool = True
    ) -> dict:
        """Initiate password recovery for one or more users.

        For every address that matches an existing user, a fresh single-use
        reset token is generated and emailed with an HMAC-signed link.

        Security measures:
        - Returns per-email results without revealing whether an address exists
            (unknown addresses report success silently to prevent enumeration)
        - Tokens are cryptographically secure random strings stored server-side
        - The emailed link embeds the token id HMAC-signed with itsdangerous, so
            the link is tamper-evident and cannot be forged or altered
        - Each token is single-use and expires after EMAIL_RESET_TOKEN_EXPIRE_HOURS
        - Existing valid tokens for the same user are invalidated before creating a new one

        Args:
            emails: Email addresses of the users requesting password recovery

        Returns:
            dict with 'sent' (addresses emailed), 'not_found' (no matching user)
            and 'failed' (email delivery errors). Callers presenting a
            non-enumerating public flow must not surface 'not_found' to end users.

        Raises:
            RuntimeError: If ``raise_if_all_fail`` is set and *every* matched
                user's email failed to send.
        """
        sent: list[str] = []
        not_found: list[str] = []
        failed: list[str] = []

        for email in emails:
            user = await self.user_repo.get_by_email(email=email)
            if not user:
                # Don't reveal if user exists for security reasons
                not_found.append(email)
                continue

            try:
                await self.send_set_password_email(user)
                sent.append(email)
            except Exception:
                failed.append(email)

        if raise_if_all_fail and failed and not sent:
            raise RuntimeError("Failed to send password reset email")

        return {"sent": sent, "not_found": not_found, "failed": failed}

    async def send_set_password_email(self, user: User, reason: str = "reset") -> None:
        """Generate a single-use token for ``user`` and email the set-password link.

        Shared by password-recovery emails (``reason="reset"``) and new-user
        invitation emails (``reason="welcome"``): both deliver an HMAC-signed,
        one-time link that lets only the recipient (who controls the mailbox)
        set the account password.

        The stored token is looked up by id; the emailed link carries an
        HMAC signature over that id (itsdangerous) so it cannot be forged or
        tampered with. One-time use is enforced server-side via the
        ``invalidated`` flag.
        """
        from app.config import settings

        # Invalidate any existing valid tokens for this user.
        # This prevents token accumulation and ensures only the latest link works.
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,  # type: ignore[arg-type]
            PasswordResetToken.invalidated.is_(False),  # type: ignore[attr-defined, arg-type]
            PasswordResetToken.expires_at > datetime.now(UTC),  # type: ignore[arg-type]
        )
        result = await self.session.execute(stmt)
        existing_tokens = result.scalars().all()
        for token_record in existing_tokens:
            token_record.invalidated = True
        if existing_tokens:
            await self.session.commit()

        # Generate a cryptographically secure random token (not JWT-based)
        reset_token = secrets.token_urlsafe(32)

        expires_at = datetime.now(UTC) + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)

        # Store the token server-side for single-use enforcement
        db_token = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at,
        )
        self.session.add(db_token)
        await self.session.commit()

        # The emailed link value is the token id HMAC-signed with itsdangerous;
        # the reset endpoint verifies the signature and looks the token up by id.
        signed_link = sign_reset_token(str(db_token.id))

        if reason == "welcome":
            email_data = generate_new_account_email(
                email_to=user.email,
                username=user.email,
                link=signed_link,
                valid_hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            )
        else:
            email_data = generate_reset_password_email(
                email_to=user.email, email=user.email, token=signed_link
            )

        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    async def reset_password(self, token: str, new_password: str) -> dict:
        """Reset a user's password using a valid single-use reset token.

        The ``token`` from the email link is an HMAC-signed value produced by
        ``sign_reset_token``. It is verified with itsdangerous (signature +
        expiry) before the underlying token record is looked up server-side.

        Security measures:
        - Link signature (HMAC) verified — forged or altered links are rejected
        - Token is looked up server-side by id and verified (not just decoded)
        - Token must not be expired or invalidated (single-use enforcement)
        - After successful use, the token is invalidated to prevent replay
        - Password complexity is enforced before processing
        - All existing reset tokens for the user are invalidated after a successful reset

        Args:
            token: Signed password reset token from the email link
            new_password: New password to set

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

        # Verify the HMAC signature/expiry on the link, then look up by id.
        token_id = verify_reset_token_link(token)
        stored_token: PasswordResetToken | None = None
        if token_id is not None:
            candidate = await self.session.get(PasswordResetToken, token_id)
            # Single-use enforcement: already-used tokens are rejected
            if candidate is not None and not candidate.invalidated:
                stored_token = candidate

        if stored_token is None:
            # Use a generic message to prevent enumeration
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token. Please request a new one.",
            )

        # Check if the token has expired
        expires = stored_token.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if expires < datetime.now(UTC):
            # Mark expired tokens as invalidated for cleanup
            stored_token.invalidated = True
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token. Please request a new one.",
            )

        # Get the user by ID (stored_token.user_id is the user's ID, not email)
        user = await self.session.get(User, stored_token.user_id)  # type: ignore[arg-type]
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
        await self.session.commit()

        # Invalidate ALL other reset tokens for this user (in case they were intercepted)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,  # type: ignore[arg-type]
            PasswordResetToken.invalidated.is_(False),  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        other_tokens = result.scalars().all()
        for other_token in other_tokens:
            other_token.invalidated = True
        if other_tokens:
            await self.session.commit()

        return {"message": "Password updated successfully"}

"""
Authentication service for handling user authentication operations.
Contains business logic for password recovery and reset.
"""

from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)


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

    async def initiate_password_recovery(self, email: str) -> None:
        """
        Initiate password recovery by generating a reset token and sending email.

        Args:
            email: Email address of the user requesting password recovery
        """
        user = await self.user_repo.get_by_email(email=email)

        if not user:
            # Don't reveal if user exists for security reasons
            return

        # Generate password reset token
        password_reset_token = generate_password_reset_token(email=email)

        # Generate email content
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )

        # Send reset password email
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    async def reset_password(self, token: str, new_password: str, session) -> dict:
        """
        Reset a user's password using a valid reset token.

        Args:
            token: Password reset token
            new_password: New password to set
            session: Database session for user lookup
        """
        # Verify the token
        email = verify_password_reset_token(token=token)
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        # Get the user by email
        user = await self.user_repo.get_by_email(email=email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

        # Update the password through the repository
        await self.user_repo.update_password(db_user=user, new_password=new_password)

        # Return success message
        return {"message": "Password updated successfully"}

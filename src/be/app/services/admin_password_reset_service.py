"""Service for admin-initiated password reset operations."""

import re

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limiter import check_rate_limit
from app.models import Message
from app.repositories.feature_flag_repo import FeatureFlagRepository
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.services.feature_flag_service import FeatureFlagService

MAX_BULK_RESET = 100


class AdminPasswordResetService:
    """Business logic for admin password reset operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def send_reset_email(self, email: str, admin_email: str) -> None:
        """Send a password reset email to the specified user.

        Validates email format, checks feature flag, enforces rate limiting,
        and delegates to AuthService for the actual token generation and email sending.

        Args:
            email: Target user's email address.
            admin_email: Email of the requesting superuser (for rate limiting).

        Raises:
            HTTPException: If email is invalid, feature flag is disabled, or rate limit exceeded.
        """
        self._validate_email(email)
        await self._check_prerequisites(admin_email)

        auth_service = self._auth_service()
        try:
            results = await auth_service.initiate_password_recovery_bulk([email])
        except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        if results["failed"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email",
            )

    async def send_reset_emails_bulk(self, user_ids: list[str], admin_email: str) -> Message:
        """Send password reset emails to multiple users selected by an admin.

        Args:
            user_ids: IDs of the users to email.
            admin_email: Email of the requesting superuser (for rate limiting).

        Returns:
            Message summarizing how many reset emails were sent.

        Raises:
            HTTPException: If the request is empty/too large, the feature flag is
                disabled, or the rate limit is exceeded.
        """
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No users selected",
            )
        if len(user_ids) > MAX_BULK_RESET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many users selected (max {MAX_BULK_RESET} per request)",
            )

        await self._check_prerequisites(admin_email)

        user_repository = UserRepository(session=self.session)
        emails: list[str] = []
        for uid in dict.fromkeys(user_ids):  # de-dupe, preserve order
            user = await user_repository.get_by_id(user_id=uid)
            if user is not None:
                emails.append(user.email)

        auth_service = self._auth_service()
        try:
            results = await auth_service.initiate_password_recovery_bulk(emails)
        except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        sent = len(results["sent"])
        failed = len(results["failed"])
        detail = f"Password reset emails sent to {sent} user(s)"
        if failed:
            detail += f"; {failed} failed to send"
        return Message(message=detail)

    # -- helpers ---------------------------------------------------------- #

    def _auth_service(self) -> AuthService:
        return AuthService(
            user_repository=UserRepository(session=self.session), session=self.session
        )

    @staticmethod
    def _validate_email(email: str) -> None:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format",
            )

    async def _check_prerequisites(self, admin_email: str) -> None:
        """Check the feature flag and enforce per-admin rate limiting."""
        flag_service = FeatureFlagService(FeatureFlagRepository(self.session))
        enabled_flags = await flag_service.get_enabled_names()
        if "enable_admin_password_reset" not in enabled_flags:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin password reset is currently disabled",
            )

        # Rate limit check (5 requests per 15 minutes per superuser)
        if not check_rate_limit(f"admin-reset:{admin_email}", 5, 15 * 60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

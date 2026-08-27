"""Service for admin-initiated password reset operations."""

import re

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limiter import check_rate_limit
from app.repositories.feature_flag_repo import FeatureFlagRepository
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.services.feature_flag_service import FeatureFlagService


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
        # Validate email format
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format",
            )

        # Check feature flag at runtime
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

        # Delegate to AuthService for token generation and email sending
        user_repository = UserRepository(session=self.session)
        auth_service = AuthService(user_repository=user_repository)
        await auth_service.initiate_password_recovery(email=email, session=self.session)

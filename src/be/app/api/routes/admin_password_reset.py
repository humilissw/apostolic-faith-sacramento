"""Routes for admin-initiated password reset."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import Message
from app.services.admin_password_reset_service import AdminPasswordResetService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin-password-reset"])


class AdminPasswordResetRequest(BaseModel):
    """Request body for admin password reset."""

    email: str = Field(..., description="Email address of the user to reset password for")


@router.post(
    "/admin/password-reset",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
async def admin_password_reset(
    body: AdminPasswordResetRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """Allow a superuser to send a password reset email to any user.

    Delegates all business logic (email validation, feature flag check,
    rate limiting, token generation, email sending) to AdminPasswordResetService.
    """
    service = AdminPasswordResetService(session=session)
    await service.send_reset_email(email=body.email, admin_email=current_user.email)

    logger.info(
        "Admin password reset initiated for %s by admin %s",
        body.email,
        current_user.email,
    )

    return Message(message="Password recovery email sent")

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


class AdminPasswordResetBulkRequest(BaseModel):
    """Request body for a bulk admin password reset."""

    user_ids: list[str] = Field(
        ..., min_length=1, description="IDs of the users to send password reset emails to"
    )


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


@router.post(
    "/admin/password-reset/bulk",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
async def admin_password_reset_bulk(
    body: AdminPasswordResetBulkRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """Allow a superuser to send password reset emails to multiple users at once.

    Each targeted user receives an email with an HMAC-signed, single-use link
    to set a new password. All business logic (feature flag check, rate
    limiting, token generation, email sending) is delegated to
    AdminPasswordResetService.
    """
    service = AdminPasswordResetService(session=session)
    result = await service.send_reset_emails_bulk(
        user_ids=body.user_ids, admin_email=current_user.email
    )

    logger.info(
        "Admin bulk password reset initiated for %d user id(s) by admin %s",
        len(body.user_ids),
        current_user.email,
    )

    return result

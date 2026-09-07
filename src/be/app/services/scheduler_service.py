"""
Scheduler service for handling assignment operations.
Contains business logic for assignment notifications and conflict management.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.config import settings
from app.utils import generate_assignment_email, send_email

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service for scheduler-related business logic.
    Handles assignment notifications and scheduling operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def send_assignment_notification(
        self,
        user_id: str,
        assignment_type: str,
        role: str,
        event_date: str,
        instrument: str | None = None,
        notes: str | None = None,
    ) -> None:
        """
        Send an email notification to a user about a new schedule assignment.

        Args:
            user_id: ID of the assigned user
            assignment_type: Type of assignment (music, service, etc.)
            role: The role assigned
            event_date: Formatted date string for the event
            instrument: Optional instrument
            notes: Optional notes
        """
        if not settings.emails_enabled:
            return

        user = await self.session.get(User, user_id)
        if not user or not user.email:
            return

        email_data = generate_assignment_email(
            email_to=user.email,
            assignment_type=assignment_type,
            role=role,
            event_date=event_date,
            instrument=instrument,
            notes=notes,
        )

        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    async def notify_assignment_safe(
        self,
        user_id: str,
        assignment_type: str,
        role: str,
        event_date: str,
        instrument: str | None = None,
        notes: str | None = None,
    ) -> None:
        """Send an assignment notification without failing the core flow.

        A delivery failure is logged (with full traceback) but never raised:
        the assignment itself has already been committed and must not be
        rolled back or reported as failed because of a notification email.
        """
        try:
            await self.send_assignment_notification(
                user_id=user_id,
                assignment_type=assignment_type,
                role=role,
                event_date=event_date,
                instrument=instrument,
                notes=notes,
            )
        except Exception:
            logger.exception(
                "Assignment notification email failed for user_id=%s (%s / %s)",
                user_id,
                assignment_type,
                role,
            )

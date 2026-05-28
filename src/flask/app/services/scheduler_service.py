from app.models import User
from app.config import settings
from app.utils import generate_assignment_email, send_email


class SchedulerService:
    def __init__(self, session):
        self.session = session

    def send_assignment_notification(
        self,
        user_id: str,
        assignment_type: str,
        role: str,
        event_date: str,
        instrument: str | None = None,
        notes: str | None = None,
    ) -> None:
        if not settings.emails_enabled:
            return
        user = self.session.get(User, user_id)
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
            email_to=user.email, subject=email_data.subject, html_content=email_data.html_content
        )

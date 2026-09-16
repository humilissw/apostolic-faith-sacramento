"""SMTP delivery for the email microservice.

Ported from src/be/app/utils.py (the backend no longer sends email). Uses the
stdlib smtplib directly so the service has a minimal dependency surface.
"""

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from jinja2 import Template

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@dataclass
class EmailData:
    subject: str
    html_content: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (TEMPLATES_DIR / template_name).read_text()
    html_content = Template(template_str).render(context)
    return str(html_content)


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """Deliver one HTML email over SMTP. Raises on any failure."""
    if not settings.smtp_configured:
        logger.error(
            "Cannot send email to %s: SMTP is not configured (SMTP_HOST/SMTP_USER empty)",
            email_to,
        )
        raise RuntimeError("Email delivery is not configured (SMTP_HOST missing)")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = email_to
    msg.set_content("This message requires an HTML-capable mail client.")
    msg.add_alternative(html_content, subtype="html")

    host = settings.SMTP_HOST or "localhost"
    port = int(settings.SMTP_PORT)
    try:
        if settings.smtp_use_ssl:
            server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            server = smtplib.SMTP(host, port, timeout=30)
        try:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(
                msg,
                from_addr=settings.EMAILS_FROM_EMAIL,
                to_addrs=email_to,
            )
        finally:
            server.quit()
    except Exception:
        logger.exception("Failed to send email to %s via %s:%s", email_to, host, port)
        raise
    logger.info("Delivered email to %s (%s)", email_to, subject)


# ── Typed generators (mirror the templates src/be used to own) ─────────


def generate_reset_password_email(email_to: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": project_name,
            "username": email_to,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, token: str, valid_hours: int | None = None
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Set up your new account"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": project_name,
            "username": username,
            "email": email_to,
            "valid_hours": valid_hours or settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_assignment_email(
    email_to: str,
    assignment_type: str,
    role: str,
    event_date: str,
    instrument: str | None = None,
    notes: str | None = None,
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Scheduler assignment"
    html_content = render_email_template(
        template_name="assignment.html",
        context={
            "project_name": project_name,
            "email": email_to,
            "assignment_type": assignment_type,
            "role": role,
            "instrument": instrument or "",
            "event_date": event_date,
            "notes": notes or "",
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": project_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_announcement_email(email_to: str, body: str) -> EmailData:
    """Plain announcement: the plaintext body is rendered as paragraphs."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Announcement"
    paragraphs = "".join(
        f"<p style='white-space:pre-wrap'>{para}</p>"
        for para in (p.strip() for p in body.split("\n\n") if p.strip())
    )
    html_content = (
        "<html><body>" f"<h2>{project_name}</h2>" f"<div>{paragraphs}</div>" "</body></html>"
    )
    return EmailData(html_content=html_content, subject=subject)

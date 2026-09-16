"""Send endpoint: the email microservice's single business route."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import CallerDep
from app.config import settings
from app.core.tracking import record_delivery
from app.core.users_db import filter_existing_users, get_all_active_user_emails
from app.requests.email_request import EmailType, SendEmailRequest, SendEmailResponse
from app.services.sender import (
    EmailData,
    generate_announcement_email,
    generate_assignment_email,
    generate_new_account_email,
    generate_reset_password_email,
    generate_test_email,
    send_email,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])


def _build_email(req: SendEmailRequest, recipient: str) -> EmailData:
    if req.type == EmailType.PASSWORD_RESET:
        assert req.token is not None
        return generate_reset_password_email(email_to=recipient, token=req.token)
    if req.type == EmailType.NEW_USER:
        assert req.token is not None
        return generate_new_account_email(
            email_to=recipient,
            username=recipient,
            token=req.token,
            valid_hours=req.valid_hours,
        )
    if req.type == EmailType.ANNOUNCEMENT:
        assert req.body is not None
        return generate_announcement_email(email_to=recipient, body=req.body)
    if req.type == EmailType.ASSIGNMENT:
        return generate_assignment_email(
            email_to=recipient,
            assignment_type=req.assignment_type or "",
            role=req.role or "",
            event_date=req.event_date or "",
            instrument=req.instrument,
            notes=req.notes,
        )
    return generate_test_email(email_to=recipient)


def _fan_out(
    *, batch_id: str, req: SendEmailRequest, recipients: list[str], caller_subject: str
) -> SendEmailResponse:
    sent: list[str] = []
    failures: list[dict] = []
    for recipient in recipients:
        email_data = _build_email(req, recipient)
        try:
            send_email(
                email_to=recipient,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        except Exception as exc:
            logger.exception("Delivery failed for %s", recipient)
            failures.append({"recipient": recipient, "error": str(exc)})
            record_delivery(
                batch_id=batch_id,
                email_type=req.type.value,
                recipient=recipient,
                subject=email_data.subject,
                status="failed",
                error=str(exc),
                requested_by=caller_subject,
            )
        else:
            sent.append(recipient)
            record_delivery(
                batch_id=batch_id,
                email_type=req.type.value,
                recipient=recipient,
                subject=email_data.subject,
                status="sent",
                requested_by=caller_subject,
            )
    return SendEmailResponse(
        batch_id=batch_id,
        type=req.type,
        sent=len(sent),
        failed=len(failures),
        recipients=sent,
        failures=failures,
    )


@router.post("/send", response_model=SendEmailResponse)
async def send_email_request(req: SendEmailRequest, caller: CallerDep) -> SendEmailResponse:
    """Send an email of the given ``type``.

    - ``password-reset`` / ``new-user``: deliver the backend-generated signed
    link (``token``) to the listed recipients. The token is opaque here —
    this service never issues or validates reset tokens, it only embeds them.
    - ``announcement``: plaintext ``body`` delivered to every active user in
    the application (or to ``recipients`` when provided). Addresses that do
    not belong to an existing active user are skipped and reported.
    - ``assignment`` / ``test``: templated notifications.

    Requires a Bearer JWT carrying the ``api:email`` scope (issued by src/be/)
    or the shared service API key.
    """
    batch_id = str(uuid.uuid4())

    if req.type == EmailType.ANNOUNCEMENT:
        if req.recipients:
            # Targeted announcement: only recipients that are NOT in the app
            # are skipped; a mix of known/unknown is delivered + reported.
            matched, unknown = filter_existing_users(req.recipients)
            if not matched:
                raise HTTPException(
                    status_code=404,
                    detail="None of the provided recipients match an active user",
                )
        else:
            matched = get_all_active_user_emails()
            unknown = []
            if not matched:
                raise HTTPException(
                    status_code=503,
                    detail="No active users found (is the shared database reachable?)",
                )
        logger.info(
            "Announcement batch %s -> %d recipient(s) (%d unknown skipped)",
            batch_id,
            len(matched),
            len(unknown),
        )
        response = _fan_out(
            batch_id=batch_id, req=req, recipients=matched, caller_subject=caller.subject
        )
        response.failures.extend({"recipient": e, "error": "not an active user"} for e in unknown)
        response.failed += len(unknown)
        return response

    if not settings.smtp_configured:
        raise HTTPException(status_code=503, detail="SMTP delivery is not configured")

    return _fan_out(
        batch_id=batch_id,
        req=req,
        recipients=[str(e) for e in (req.recipients or [])],
        caller_subject=caller.subject,
    )

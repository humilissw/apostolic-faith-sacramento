"""HTTP client for the src/email/ microservice.

The backend no longer talks to SMTP itself; every email is delegated to the
email service over HTTP. This module forwards the calling user's JWT when one
is available (so the email service can enforce its ``api:email`` scope against
the actual caller), falling back to the shared service API key for flows with
no authenticated caller (e.g. public password-recovery).

The backend generates reset/set-password tokens; the email service only embeds
them in the delivered links.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# The presented token of the in-flight request (cookie or Authorization
# header), captured by RequestAuthContextMiddleware so service-layer code can
# forward the caller's identity to the email microservice.
caller_token_var: ContextVar[str | None] = ContextVar("email_caller_token", default=None)


class RequestAuthContextMiddleware:
    """Pure-ASGI middleware recording the request's bearer/cookie token.

    Sets ``caller_token_var`` before invoking the inner app in the same task
    context, so handlers/services deeper in the request can read it (pure ASGI
    avoids the BaseHTTPMiddleware contextvar-propagation pitfalls).
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") == "http":
            headers = {
                k.decode("latin-1").lower(): v.decode("latin-1")
                for k, v in scope.get("headers", [])
            }
            token: str | None = None
            cookie_header = headers.get("cookie", "")
            for part in cookie_header.split(";"):
                name, _, value = part.strip().partition("=")
                if name == settings.ACCESS_TOKEN_COOKIE_NAME and value:
                    token = value
                    break
            auth_header = headers.get("authorization", "")
            if not token and auth_header.startswith("Bearer "):
                token = auth_header[7:]
            caller_token_var.set(token)
        await self.app(scope, receive, send)


class EmailServiceError(RuntimeError):
    """Raised when the email microservice rejects or cannot handle a request."""


def build_send_payload(
    *,
    email_type: str,
    recipients: list[str] | None = None,
    token: str | None = None,
    body: str | None = None,
    valid_hours: int | None = None,
    **template_fields: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"type": email_type}
    if recipients:
        payload["recipients"] = list(recipients)
    if token is not None:
        payload["token"] = token
    if body is not None:
        payload["body"] = body
    if valid_hours is not None:
        payload["valid_hours"] = valid_hours
    payload.update({k: v for k, v in template_fields.items() if v is not None})
    return payload


async def send_email_request(**kwargs: Any) -> dict[str, Any]:
    """POST to the email microservice's /email/send. Raises EmailServiceError."""
    base = settings.EMAIL_SERVICE_URL.strip().rstrip("/")
    if not base:
        logger.error("Cannot send email: EMAIL_SERVICE_URL is not configured")
        raise EmailServiceError("Email delivery is not configured (EMAIL_SERVICE_URL missing)")

    headers: dict[str, str] = {"Content-Type": "application/json"}
    caller_token = caller_token_var.get()
    if caller_token:
        headers["Authorization"] = f"Bearer {caller_token}"
    elif settings.EMAIL_SERVICE_API_KEY:
        headers["X-API-Key"] = settings.EMAIL_SERVICE_API_KEY
    else:
        raise EmailServiceError("No caller token or email service API key available for delivery")

    url = f"{base}/api/v1/email/send"
    payload = build_send_payload(**kwargs)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
    except httpx.HTTPError:
        logger.exception("Email service request to %s failed", url)
        raise EmailServiceError(f"Email service unreachable at {url}")

    if response.status_code >= 400:
        detail = ""
        try:
            detail = str(response.json().get("detail", ""))
        except Exception:  # noqa: BLE001
            detail = response.text[:200]
        logger.error(
            "Email service rejected %s request (%s): %s",
            payload.get("type"),
            response.status_code,
            detail,
        )
        raise EmailServiceError(f"Email service error {response.status_code}: {detail}")

    result: dict[str, Any] = response.json()
    logger.info(
        "Email service delivered type=%s sent=%s failed=%s batch=%s",
        payload.get("type"),
        result.get("sent"),
        result.get("failed"),
        result.get("batch_id"),
    )
    return result

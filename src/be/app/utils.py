"""Utility helpers for the backend.

Email delivery now lives in the src/email/ microservice (see
app/services/email_client.py): this module no longer renders templates or
talks to SMTP — it only keeps password-reset JWT helpers used by auth flows.
"""

import logging
from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings
from app.core import security

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        security.PRIVATE_KEY,
        algorithm=security.ALGORITHM,
    )
    return str(encoded_jwt)


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(token, security.PUBLIC_KEY, algorithms=[security.ALGORITHM])
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None

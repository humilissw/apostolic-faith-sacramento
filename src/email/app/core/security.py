"""JWT verification for the email microservice.

The email service never issues tokens. It verifies RS256 JWTs issued by the
src/be/ backend using that service's public key, and requires the
``api:email`` scope on every send request. A shared service API key is also
accepted for trusted server-to-server calls (e.g. unauthenticated
password-recovery flows where no user token exists).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import jwt

from app.config import settings


@lru_cache(maxsize=1)
def public_key() -> str:
    """PEM contents of the backend's RSA public key (verification only)."""
    return Path(settings.RSA_PUB_KEY).read_text()


def decode_token(token: str) -> dict:
    """Decode and verify a backend-issued JWT.

    Raises ``jwt.InvalidTokenError`` on any verification failure.
    """
    decode_kwargs: dict = {}
    if settings.JWT_AUDIENCE:
        decode_kwargs["audience"] = settings.JWT_AUDIENCE
    if settings.JWT_ISSUER:
        decode_kwargs["issuer"] = settings.JWT_ISSUER
    payload: dict = jwt.decode(token, public_key(), algorithms=["RS256"], **decode_kwargs)
    return payload


def has_email_scope(payload: dict) -> bool:
    scopes = payload.get("scopes") or []
    return settings.EMAIL_REQUIRED_SCOPE in scopes


def is_superuser_token(payload: dict) -> bool:
    scopes = payload.get("scopes") or []
    return "superuser" in scopes

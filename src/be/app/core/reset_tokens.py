"""HMAC-signed password reset tokens.

Uses ``itsdangerous`` (the itsdangerous library) to produce signed, URL-safe
tokens for password reset links:

- The token payload is the reset token's database id; the signature (HMAC via
    ``SECRET_KEY``) makes the link tamper-evident — a user cannot forge or alter
    another user's reset link.
- A dedicated salt separates reset tokens from any other signed value in the
    app, so signatures are not interchangeable across purposes.
- Expiry is enforced by ``TimestampSigner`` using
    ``EMAIL_RESET_TOKEN_EXPIRE_HOURS``.

One-time usage is still enforced server-side by the ``password_reset_tokens``
table (the ``invalidated`` flag); the signature only guarantees the link could
not be forged or modified in transit.
"""

from functools import lru_cache

from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

from app.config import settings


@lru_cache(maxsize=1)
def _signer() -> TimestampSigner:
    return TimestampSigner(settings.SECRET_KEY, salt="password-reset-token")


def sign_reset_token(token_id: str) -> str:
    """Return an HMAC-signed, URL-safe string for the given reset token id."""
    signed: bytes = _signer().sign(str(token_id).encode("utf-8"))
    return signed.decode("utf-8")


def verify_reset_token_link(signed: str) -> str | None:
    """Validate a signed reset link value.

    Returns the reset token's database id when the signature is valid and the
    link has not expired; ``None`` otherwise (forged, altered, or stale link).
    """
    max_age = settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS * 3600
    try:
        value = _signer().unsign(signed.encode("utf-8"), max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)

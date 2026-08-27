"""Server-side authentication primitives for the BFF.

The BFF keeps JWTs out of the browser entirely:

* On login it authenticates against the backend, stores the tokens in a signed Flask session cookie,
mints a short-lived **one-time auth code**, and redirects the browser to the SPA with ``?code=...``.
* The SPA exchanges that code for an opaque session (the same cookie), after which every request is
authenticated by the BFF injecting the access token as an ``Authorization: *** header toward the
backend.

Auth codes are stored in-process (single-instance) and consumed exactly once.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

# Keys used inside the Flask session to hold tokens / user info (not secret values).
ACCESS_TOKEN_KEY = "access_token"  # nosec B105 -- session key name, not a password
REFRESH_TOKEN_KEY = "refresh_token"  # nosec B105 -- session key name, not a password
USER_KEY = "user"


@dataclass
class _AuthCode:
    """A pending one-time login code, optionally carrying bound metadata."""

    code: str
    created_at: float
    consumed: bool = False
    metadata: dict = field(default_factory=dict)


# In-memory store of issued codes. Keyed by code string.
_CODES: dict[str, _AuthCode] = {}


def _purge_expired(ttl_seconds: int) -> None:
    """Drop expired / long-consumed codes to keep the store bounded."""
    now = time.time()
    stale = [c for c in _CODES.values() if now - c.created_at > ttl_seconds * 2]
    for entry in stale:
        _CODES.pop(entry.code, None)


def issue_auth_code(ttl_seconds: int, metadata: dict | None = None) -> str:
    """Create and return a fresh one-time auth code.

    ``metadata`` (e.g. the login ticket / email) is bound to the code so the
    consumer can later verify which session it was issued to.
    """
    _purge_expired(ttl_seconds)
    code = secrets.token_urlsafe(32)
    _CODES[code] = _AuthCode(code=code, created_at=time.time(), metadata=dict(metadata or {}))
    return code


def consume_auth_code(code: str | None, ttl_seconds: int) -> dict | None:
    """Consume a one-time auth code.

    Returns the code's bound ``metadata`` dict if the code was valid and is now
    marked consumed; ``None`` for unknown, expired, or already-used codes (which
    are also removed). Guarantees single-use semantics.
    """
    if not code:
        return None
    entry = _CODES.pop(code, None)
    if entry is None:
        return None
    if entry.consumed or time.time() - entry.created_at > ttl_seconds:
        return None
    return dict(entry.metadata)


def reset_auth_codes() -> None:
    """Clear all issued codes (used by tests)."""
    _CODES.clear()


# --------------------------------------------------------------------------- #
#  Session helpers                                                            #
# --------------------------------------------------------------------------- #


@dataclass
class StoredSession:
    """Tokens + user info held in the Flask session."""

    access_token: str = ""
    refresh_token: str = ""
    user: dict = field(default_factory=dict)

    @property
    def authenticated(self) -> bool:
        return bool(self.access_token)


def session_get(session) -> StoredSession:  # type: ignore[no-untyped-def]
    """Read the stored session from a Flask ``session`` proxy."""
    return StoredSession(
        access_token=session.get(ACCESS_TOKEN_KEY, "") or "",
        refresh_token=session.get(REFRESH_TOKEN_KEY, "") or "",
        user=dict(session.get(USER_KEY) or {}),
    )


def session_set(session, stored: StoredSession) -> None:  # type: ignore[no-untyped-def]
    """Write a :class:`StoredSession` into the Flask ``session`` proxy."""
    session[ACCESS_TOKEN_KEY] = stored.access_token
    session[REFRESH_TOKEN_KEY] = stored.refresh_token
    session[USER_KEY] = stored.user


def session_clear(session) -> None:  # type: ignore[no-untyped-def]
    """Remove all BFF auth data from the Flask ``session`` proxy."""
    for key in (ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY):
        session.pop(key, None)

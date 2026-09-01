"""BFF configuration, sourced from environment variables.

Every value has a sensible local-dev default so the server runs with zero
configuration; production must override ``SECRET_KEY`` and (typically)
``BACKEND_URL`` / ``SPA_ORIGINS``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


def _parse_list(value: str) -> list[str]:
    """Parse a comma-separated or JSON-array string into a list of origins."""
    value = (value or "").strip()
    if not value:
        return []
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(o).strip() for o in parsed if str(o).strip()]
        except (json.JSONDecodeError, ValueError):
            pass
    return [o.strip() for o in value.split(",") if o.strip()]


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # --- Upstream FastAPI backend ------------------------------------------- #
    #: Base URL of the backend (trailing slash normalized away).
    BACKEND_URL: str = "https://localhost:8000"
    #: Verify the backend's TLS certificate. Self-signed dev certs require this
    #: to be False (mirrors ``infrastructure/health_edge.py``). For a real CA in
    #: production, keep True and point ``BACKEND_CA_BUNDLE`` at the bundle.
    BACKEND_VERIFY: bool = True
    #: Optional path to a CA bundle used to verify the backend certificate.
    BACKEND_CA_BUNDLE: str | None = None

    # --- SPA ---------------------------------------------------------------- #
    #: Public origin(s) of the Next.js SPA, used for CORS + default redirect.
    SPA_ORIGINS: list[str] = field(default_factory=lambda: ["https://localhost:3000"])
    #: Base URL the browser is sent back to after a successful login.
    SPA_URL: str = "https://localhost:3000"

    # --- Session / signing -------------------------------------------------- #
    #: Signs Flask sessions and one-time auth codes. REQUIRED in production.
    SECRET_KEY: str | None = None
    SESSION_COOKIE_NAME: str = "bff_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_HTTPONLY: bool = True

    # --- Auth codes --------------------------------------------------------- #
    #: Lifetime (seconds) of the one-time code handed to the SPA on login.
    AUTH_CODE_TTL_SECONDS: int = 120

    # --- Outbound ----------------------------------------------------------- #
    #: Timeout (seconds) for requests forwarded to the backend.
    BACKEND_TIMEOUT: float = 30.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "BACKEND_URL", self.BACKEND_URL.rstrip("/"))


def load_settings() -> Settings:
    """Build a :class:`Settings` from the current environment."""
    return Settings(
        BACKEND_URL=os.environ.get("BACKEND_URL", "https://localhost:8000"),
        BACKEND_VERIFY=_bool("BACKEND_VERIFY", True),
        BACKEND_CA_BUNDLE=os.environ.get("BACKEND_CA_BUNDLE") or None,
        SPA_ORIGINS=_parse_list(os.environ.get("SPA_ORIGINS", "")) or ["https://localhost:3000"],
        SPA_URL=os.environ.get("SPA_URL", "https://localhost:3000").rstrip("/"),
        SECRET_KEY=os.environ.get("SECRET_KEY") or None,
        SESSION_COOKIE_NAME=os.environ.get("SESSION_COOKIE_NAME", "bff_session"),
        SESSION_COOKIE_SECURE=_bool("SESSION_COOKIE_SECURE", True),
        SESSION_COOKIE_SAMESITE=os.environ.get("SESSION_COOKIE_SAMESITE", "Lax"),
        SESSION_COOKIE_HTTPONLY=_bool("SESSION_COOKIE_HTTPONLY", True),
        AUTH_CODE_TTL_SECONDS=int(os.environ.get("AUTH_CODE_TTL_SECONDS", "120")),
        BACKEND_TIMEOUT=float(os.environ.get("BACKEND_TIMEOUT", "30")),
    )

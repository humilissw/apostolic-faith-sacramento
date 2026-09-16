"""Read-only access to the shared application database (``users`` table).

The email service shares the backend's MySQL database until user management is
extracted into its own microservice. Access here is deliberately limited to
the queries email delivery needs (recipient lookup for announcements and
existence checks); nothing in this module writes to the shared database —
delivery tracking lives in the service-owned tracking database (app.core.tracking).
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import settings


@lru_cache(maxsize=1)
def users_engine() -> Engine:
    return create_engine(settings.USERS_DB_URL, pool_pre_ping=True, pool_recycle=3600)


def get_all_active_user_emails() -> list[str]:
    """Email addresses of every active user in the application."""
    with users_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT email FROM users WHERE is_active = 1 ORDER BY created_on")
        ).fetchall()
    return [str(row[0]) for row in rows]


def filter_existing_users(emails: list[str]) -> tuple[list[str], list[str]]:
    """Split ``emails`` into (known, unknown) using the shared users table.

    Matching is case-insensitive on email address. Returns ([], [])-style
    empty lists only when no addresses match.
    """
    if not emails:
        return [], []

    with users_engine().connect() as conn:
        rows = conn.execute(text("SELECT LOWER(email) FROM users WHERE is_active = 1")).fetchall()
    known = {str(row[0]) for row in rows}
    matched = [e for e in emails if e.strip().lower() in known]
    unmatched = [e for e in emails if e.strip().lower() not in known]
    return matched, unmatched

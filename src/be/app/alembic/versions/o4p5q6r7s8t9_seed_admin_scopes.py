"""seed superuser account and all application scopes

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-05-30

"""

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "o4p5q6r7s8t9"
down_revision: Union[str, Sequence[str], None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All application scopes from app/core/scopes.py (Scope enum values)
ALL_SCOPES = [
    "api:all",
    "spa:all",
    "mobile:all",
    "public:read",
    "payments:read",
    "payments:write",
    "payments:admin",
    "integrations:admin",
    "video_uploads:read",
    "video_uploads:write",
    "video_uploads:delete",
    "video_uploads:manage",
    "users:read",
    "users:write",
    "users:admin",
    "scheduler:admin",
    "member:limited",
    "superuser",
    "client",
]

FIRST_SUPERUSER_EMAIL = "admin@example.com"
FIRST_SUPERUSER_PASSWORD = "!maSup3rUs3r1!"

# bcrypt hash of FIRST_SUPERUSER_PASSWORD, generated with passlib
FIRST_SUPERUSER_HASHED_PASSWORD = "$2b$12$6nti9sIUHIgGjoruqNy46.0Xp/CFcox2UiEKLaUg9jBJ1ZnndNCxO"


def _gen_uuid_str() -> str:
    """Generate a raw UUID string for inlining into SQL."""
    return str(uuid.uuid4())


def _quote(s: str) -> str:
    """Return SQL-safe quoted string literal."""
    escaped = s.replace("'", "''")
    return "'" + escaped + "'"


def _execute(conn, sql: str) -> None:
    """Execute a raw SQL string (MariaDB-safe, no bind params on id columns)."""
    conn.execute(sa.text(sql))  # type: ignore[arg-type]


def _row(conn, sql: str) -> tuple | None:
    """Execute SQL and return first row or None."""
    result = conn.execute(sa.text(sql)).fetchone()
    return result  # type: ignore[no-any-return]


def upgrade() -> None:
    conn = op.get_bind()

    # Check if user already exists
    email_q = _quote(FIRST_SUPERUSER_EMAIL)
    query: str = f"SELECT `id` FROM `users` WHERE `email` = {email_q} LIMIT 1"
    row = _row(conn, query)

    if row is None:
        # Create the superuser with inline UUIDs
        # MariaDB coerces string UUID bind params to integers on id columns -> truncation
        uid = _gen_uuid_str()
        new_id = _gen_uuid_str()
        pw_q = _quote(FIRST_SUPERUSER_HASHED_PASSWORD)
        email_q2 = _quote(FIRST_SUPERUSER_EMAIL)
        insert_query: str = (
            f"INSERT INTO `users` (`id`, `email`, `is_active`, `is_superuser`, "
            f"`hashed_password`, `created_on`, `updated_on`, `new_id`) "
            f"VALUES ('{uid}', {email_q2}, 1, 1, {pw_q}, NOW(), NULL, '{new_id}')"
        )
        _execute(conn, insert_query)
        row = (uid,)

    user_id = row[0]

    # Get existing scopes
    uid_q = _quote(str(user_id))
    scopes_query: str = f"SELECT `scope` FROM `user_scopes` WHERE `user_id` = {uid_q}"
    result = conn.execute(sa.text(scopes_query))
    existing_scopes = {r[0] for r in result}

    # Insert missing scopes with inline UUID() function (no bind params on id columns)
    for scope in ALL_SCOPES:
        if scope not in existing_scopes:
            scope_q = _quote(scope)
            insert_sql: str = (
                f"INSERT IGNORE INTO `user_scopes` (`id`, `user_id`, `scope`, `created_on`) "
                f"VALUES (UUID(), {uid_q}, {scope_q}, NOW())"
            )
            _execute(conn, insert_sql)


def downgrade() -> None:
    conn = op.get_bind()

    email_q = _quote(FIRST_SUPERUSER_EMAIL)
    query: str = f"SELECT `id` FROM `users` WHERE `email` = {email_q} LIMIT 1"
    row = _row(conn, query)

    if row is None:
        return

    user_id = row[0]
    uid_q = _quote(str(user_id))

    scope_qs = ", ".join(_quote(s) for s in ALL_SCOPES)
    delete_query: str = (
        f"DELETE FROM `user_scopes` WHERE `user_id` = {uid_q} AND `scope` IN ({scope_qs})"
    )
    _execute(conn, delete_query)

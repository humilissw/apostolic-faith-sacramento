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


def _execute(conn, sql: str) -> None:
    """Execute a raw SQL string (MariaDB-safe, no bind params on id columns)."""
    conn.execute(sa.text(sql))  # type: ignore[arg-type]


def upgrade() -> None:
    conn = op.get_bind()

    # Check if user already exists
    query: str = "SELECT `id` FROM `users` WHERE `email` = %s LIMIT 1" % FIRST_SUPERUSER_EMAIL
    row = conn.execute(sa.text(query)).fetchone()

    if row is None:
        # Create the superuser with inline UUIDs
        # MariaDB coerces string UUID bind params to integers on id columns -> truncation
        uid = _gen_uuid_str()
        new_id = _gen_uuid_str()
        insert_query: str = (
            "INSERT INTO `users` (`id`, `email`, `is_active`, `is_superuser`, "
            "`hashed_password`, `created_on`, `updated_on`, `new_id`) "
            "VALUES (%s, %s, 1, 1, %s, NOW(), NULL, %s)"
        ) % (uid, FIRST_SUPERUSER_EMAIL, FIRST_SUPERUSER_HASHED_PASSWORD, new_id)
        _execute(conn, insert_query)
        row = (uid,)

    user_id = row[0]

    # Get existing scopes
    scopes_query: str = "SELECT `scope` FROM `user_scopes` WHERE `user_id` = %s" % user_id
    result = conn.execute(sa.text(scopes_query))
    existing_scopes = {r[0] for r in result}

    # Insert missing scopes with inline UUID() function (no bind params on id columns)
    for scope in ALL_SCOPES:
        if scope not in existing_scopes:
            insert_query_2: str = (
                "INSERT IGNORE INTO `user_scopes` (`id`, `user_id`, `scope`, `created_on`) "
                "VALUES (UUID(), %s, %s, NOW())"
            ) % (user_id, scope)
            _execute(conn, insert_query_2)


def downgrade() -> None:
    conn = op.get_bind()

    query: str = "SELECT `id` FROM `users` WHERE `email` = %s LIMIT 1" % FIRST_SUPERUSER_EMAIL
    row = conn.execute(sa.text(query)).fetchone()

    if row is None:
        return

    user_id = row[0]

    placeholders = ", ".join(["%s" for _ in ALL_SCOPES])
    delete_query: str = "DELETE FROM `user_scopes` WHERE `user_id` = %s AND `scope` IN (%s)" % (
        user_id,
        placeholders,
    )
    delete_query = delete_query % tuple(ALL_SCOPES)
    _execute(conn, delete_query)

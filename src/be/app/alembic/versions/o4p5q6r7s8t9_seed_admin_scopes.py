"""seed superuser scopes with all application scopes

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-05-30

"""

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


def upgrade() -> None:
    conn = op.get_bind()

    # Get the user id for the first superuser
    result = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email LIMIT 1").bindparams(
            email=FIRST_SUPERUSER_EMAIL
        )
    )
    row = result.fetchone()

    if row is None:
        return

    user_id = row[0]

    # Check which scopes already exist for this user
    existing = conn.execute(
        sa.text("SELECT scope FROM user_scopes WHERE user_id = :uid").bindparams(uid=user_id)
    )
    existing_scopes = {r[0] for r in existing}

    # Insert missing scopes
    to_insert = [scope for scope in ALL_SCOPES if scope not in existing_scopes]

    if not to_insert:
        return

    for scope in to_insert:
        conn.execute(
            sa.text(
                "INSERT IGNORE INTO user_scopes (id, user_id, scope, created_on) VALUES (UUID(), :sid, :sc, NOW())"
            ).bindparams(sid=user_id, sc=scope)
        )


def downgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email LIMIT 1").bindparams(
            email=FIRST_SUPERUSER_EMAIL
        )
    )
    row = result.fetchone()

    if row is None:
        return

    user_id = row[0]

    placeholders = ", ".join(f":scope_{i}" for i in range(len(ALL_SCOPES)))
    query = "DELETE FROM user_scopes " f"WHERE user_id = :uid AND scope IN ({placeholders})"
    params = {"uid": user_id}
    for i, scope in enumerate(ALL_SCOPES):
        params[f"scope_{i}"] = scope

    conn.execute(sa.text(query).bindparams(**params))

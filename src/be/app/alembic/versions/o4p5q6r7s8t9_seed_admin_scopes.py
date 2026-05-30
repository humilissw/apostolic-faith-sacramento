"""seed superuser account and all application scopes

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
FIRST_SUPERUSER_PASSWORD = "!maSup3rUs3r1!"

# bcrypt hash of FIRST_SUPERUSER_PASSWORD, generated with passlib
FIRST_SUPERUSER_HASHED_PASSWORD = "$2b$12$6nti9sIUHIgGjoruqNy46.0Xp/CFcox2UiEKLaUg9jBJ1ZnndNCxO"


def upgrade() -> None:
    conn = op.get_bind()

    # Check if user already exists
    user_id = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email LIMIT 1").bindparams(
            email=FIRST_SUPERUSER_EMAIL
        )
    ).fetchone()

    if user_id is None:
        # Create the superuser
        new_uid = str(op.get_bind().execute(sa.text("SELECT UUID()")).fetchone()[0])
        conn.execute(
            sa.text(
                "INSERT INTO users (id, email, is_active, is_superuser, hashed_password, created_on, updated_on, new_id) "
                "VALUES (:uid, :email, 1, 1, :pw, NOW(), NULL, :new_id)"
            ).bindparams(
                uid=new_uid,
                email=FIRST_SUPERUSER_EMAIL,
                pw=FIRST_SUPERUSER_HASHED_PASSWORD,
                new_id=str(op.get_bind().execute(sa.text("SELECT UUID()")).fetchone()[0]),
            )
        )
        user_id = new_uid
    else:
        user_id = user_id[0]

    # Get existing scopes
    result = conn.execute(
        sa.text("SELECT scope FROM user_scopes WHERE user_id = :uid").bindparams(uid=user_id)
    )
    existing_scopes = {r[0] for r in result}

    # Insert missing scopes
    for scope in ALL_SCOPES:
        if scope not in existing_scopes:
            conn.execute(
                sa.text(
                    "INSERT IGNORE INTO user_scopes (id, user_id, scope, created_on) VALUES (UUID(), :uid, :sc, NOW())"
                ).bindparams(uid=user_id, sc=scope)
            )


def downgrade() -> None:
    conn = op.get_bind()

    user_id = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email LIMIT 1").bindparams(
            email=FIRST_SUPERUSER_EMAIL
        )
    ).fetchone()

    if user_id is None:
        return

    user_id = user_id[0]

    placeholders = ", ".join(f":scope_{i}" for i in range(len(ALL_SCOPES)))
    query = "DELETE FROM user_scopes " f"WHERE user_id = :uid AND scope IN ({placeholders})"
    params = {"uid": user_id}
    for i, scope in enumerate(ALL_SCOPES):
        params[f"scope_{i}"] = scope

    conn.execute(sa.text(query).bindparams(**params))

"""seed admin user

Revision ID: p1q2r3s4t5u6
Revises: n3o4p5q6r7s8
Create Date: 2026-05-28

Seeds the FIRST_SUPERUSER from .env into the users table as a
superuser with all available scopes. Idempotent via ON DUPLICATE KEY UPDATE.

"""

import os
from typing import Sequence, Union

from alembic import op
from dotenv import load_dotenv
from pathlib import Path
from pwdlib import PasswordHash
from sqlalchemy import text

# Revision identifiers
revision: str = "p1q2r3s4t5u6"
down_revision: Union[str, Sequence[str], None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All scopes from backend.core.scopes.Scope enum
_ALL_SCOPES = [
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


def upgrade() -> None:
    load_dotenv(Path(__file__).parent.parent / ".env", override=True)

    first_superuser = os.getenv("FIRST_SUPERUSER")
    first_superuser_password = os.getenv("FIRST_SUPERUSER_PASSWORD")

    if not first_superuser or not first_superuser_password:
        return

    hashed_pw = PasswordHash.recommended().hash(first_superuser_password)

    conn = op.get_bind()

    # Seed user (idempotent)
    conn.execute(
        text(
            "INSERT INTO users "
            "(id, new_id, email, hashed_password, is_active, is_superuser, full_name, created_on, updated_on) "
            "VALUES (UUID(), UUID(), :email, :hashed_pw, 1, 1, NULL, NOW(), NULL) "
            "ON DUPLICATE KEY UPDATE is_superuser = 1, hashed_password = VALUES(hashed_password)"
        ),
        {"email": first_superuser, "hashed_pw": hashed_pw},
    )

    # Get user ID (INSERT or already existed)
    user = conn.execute(
        text("SELECT id FROM users WHERE email = :email LIMIT 1"),
        {"email": first_superuser},
    ).fetchone()
    if not user:
        return

    user_id = user[0]

    # Insert all scopes for this user (idempotent)
    for scope in _ALL_SCOPES:
        conn.execute(
            text(
                "INSERT INTO user_scopes (id, user_id, scope, created_on) "
                "VALUES (UUID(), :user_id, :scope, NOW()) "
                "ON DUPLICATE KEY UPDATE scope = VALUES(scope)"
            ),
            {"user_id": user_id, "scope": scope},
        )


def downgrade() -> None:
    first_superuser = os.getenv("FIRST_SUPERUSER")
    if first_superuser:
        conn = op.get_bind()
        conn.execute(
            text("DELETE FROM users WHERE email = :email"),
            {"email": first_superuser},
        )
        conn.execute(
            text("DELETE FROM user_scopes WHERE user_id = " "(SELECT id FROM users WHERE email = :email)"),
            {"email": first_superuser},
        )

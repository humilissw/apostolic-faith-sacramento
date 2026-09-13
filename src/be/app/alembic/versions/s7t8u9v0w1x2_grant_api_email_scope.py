"""grant api:email scope to all existing users

Adds the ``api:email`` scope (required by the src/email/ microservice) to
every existing user. This is a temporary blanket grant so the email-service
cutover does not lock anyone out; later this scope should be assigned by role.

Revision ID: s7t8u9v0w1x2
Revises: r6s7t8u9v0w1
Create Date: 2026-09-13

"""

from typing import Sequence, Union

from alembic import op

revision: str = "s7t8u9v0w1x2"
down_revision: Union[str, Sequence[str], None] = "r6s7t8u9v0w1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Idempotent insert: one api:email row per user that lacks it.
    op.execute("""
        INSERT INTO user_scopes (id, user_id, scope, created_on)
        SELECT UUID(), u.id, 'api:email', NOW()
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM user_scopes s
            WHERE s.user_id = u.id AND s.scope = 'api:email'
        )
        """)


def downgrade() -> None:
    op.execute("DELETE FROM user_scopes WHERE scope = 'api:email'")

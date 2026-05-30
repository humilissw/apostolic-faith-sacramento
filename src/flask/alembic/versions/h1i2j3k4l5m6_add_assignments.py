"""add assignments table and seed member:limited scope

Revision ID: h1i2j3k4l5m6
Revises: g1h2i3j4k5l6
Create Date: 2026-05-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "h1i2j3k4l5m6"
down_revision: Union[str, Sequence[str], None] = "g1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create assignments table (ignore if exists from previous partial run)
    try:
        op.create_table(
            "assignments",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("event_date", sa.DateTime(), nullable=False),
            sa.Column("type", sa.String(length=10), nullable=False),
            sa.Column("role", sa.String(length=200), nullable=False, server_default=""),
            sa.Column("instrument", sa.String(length=200), nullable=True),
            sa.Column("notes", sa.String(length=4000), nullable=True),
            sa.Column("created_on", sa.DateTime(), nullable=False),
            sa.Column("updated_on", sa.DateTime(), nullable=True),
        )
        op.create_index(op.f("ix_assignments_user_id"), "assignments", ["user_id"])
        op.create_index(op.f("ix_assignments_event_date"), "assignments", ["event_date"])
    except Exception:
        pass

    # Seed member:limited scope for existing users without it
    try:
        op.execute(
            """
            INSERT INTO user_scopes (id, user_id, scope, created_on)
            SELECT UUID(), id, 'member:limited', NOW()
            FROM users
            WHERE id NOT IN (
                SELECT user_id FROM user_scopes WHERE scope = 'member:limited'
            )
            """
        )
    except Exception:
        pass


def downgrade() -> None:
    op.drop_table("assignments")
    try:
        op.execute("DELETE FROM user_scopes WHERE scope = 'member:limited'")
    except Exception:
        pass

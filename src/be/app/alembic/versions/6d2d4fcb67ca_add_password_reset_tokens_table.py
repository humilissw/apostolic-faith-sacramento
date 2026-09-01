"""add_password_reset_tokens_table

Revision ID: 6d2d4fcb67ca
Revises: n3o4p5q6r7s8
Create Date: 2026-08-07 22:48:49.414400

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d2d4fcb67ca"
down_revision: Union[str, Sequence[str], None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create password_reset_tokens table for server-side token tracking."""
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("token", sa.String(length=4000), nullable=False, unique=True, index=True),
        sa.Column("invalidated", sa.Boolean(), nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Drop password_reset_tokens table."""
    op.drop_table("password_reset_tokens")

"""add refresh token table

Revision ID: 0001_add_refresh_token
Revises:
Create Date: 2026-05-02

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_add_refresh_token"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create refresh_token table."""
    op.create_table(
        "refreshtoken",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=4000), nullable=False, unique=True),
        sa.Column("revoked", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_on", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Drop refresh_token table."""
    op.drop_index("ix_refreshtoken_user_id", table_name="refreshtoken")
    op.drop_index("ix_refreshtoken_token", table_name="refreshtoken")
    op.drop_table("refreshtoken")

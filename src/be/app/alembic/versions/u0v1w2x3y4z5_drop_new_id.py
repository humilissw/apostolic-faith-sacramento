"""drop unused new_id column from users table

Revision ID: u0v1w2x3y4z5
Revises: o4p5q6r7s8t9
Create Date: 2026-05-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "u0v1w2x3y4z5"
down_revision: Union[str, Sequence[str], None] = "o4p5q6r7s8t9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "new_id")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("new_id", sa.String(length=36), nullable=False, server_default=""),
    )

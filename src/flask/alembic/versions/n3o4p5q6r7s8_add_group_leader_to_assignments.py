"""add group_leader to assignments

Revision ID: n3o4p5q6r7s8
Revises: n2o3p4q5r6s7
Create Date: 2026-05-11

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Boolean, Column as sa_Column

revision: str = "n3o4p5q6r7s8"
down_revision: Union[str, Sequence[str], None] = "n2o3p4q5r6s7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assignments",
        sa_Column("group_leader", Boolean(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("assignments", "group_leader")

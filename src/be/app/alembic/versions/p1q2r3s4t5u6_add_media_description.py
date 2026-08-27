"""add description column to media table

Revision ID: p1q2r3s4t5u6
Revises: 6d2d4fcb67ca
Create Date: 2026-08-21 14:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "p1q2r3s4t5u6"
down_revision: Union[str, Sequence[str], None] = "6d2d4fcb67ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "media",
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=4000), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("media", "description")

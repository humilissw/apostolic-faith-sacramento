"""add owner_id to media and video_uploads

Revision ID: a1b2c3d4e5f6
Revises: 482d25a6fc5d
Create Date: 2026-05-03 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "5bedd612693f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add owner_id column to media and video_uploads tables."""
    op.add_column(
        "media",
        sa.Column(
            "owner_id",
            sqlmodel.sql.sqltypes.AutoString(length=36),
            nullable=False,
            server_default="00000000-0000-0000-0000-000000000000",
        ),
    )
    op.add_column(
        "video_uploads",
        sa.Column(
            "owner_id",
            sqlmodel.sql.sqltypes.AutoString(length=36),
            nullable=False,
            server_default="00000000-0000-0000-0000-000000000000",
        ),
    )


def downgrade() -> None:
    """Remove owner_id columns."""
    op.drop_column("video_uploads", "owner_id")
    op.drop_column("media", "owner_id")

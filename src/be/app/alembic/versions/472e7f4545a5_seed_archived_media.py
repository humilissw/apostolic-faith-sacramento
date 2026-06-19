"""seed archived media

Revision ID: 472e7f4545a5
Revises: 380009a5732b
Create Date: 2026-06-18 17:09:04.631836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import os
import json
from app.config import settings


# revision identifiers, used by Alembic.
revision: str = '472e7f4545a5'
down_revision: Union[str, Sequence[str], None] = '380009a5732b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    archived_media = os.path.expanduser(settings.ARCHIVED_MEDIA)
    with open(archived_media) as f: 
        data = json.load(f)
    
    media = [
        {"id": key, "file_location": value}
        for key, value in data.items()
        if "zoom" not in value
    ]

    archived_media_table = sa.table(
        'archived_media',
        sa.column('id', sa.String),
        sa.column('file_location', sa.String)
    )

    op.bulk_insert(archived_media_table, media)



def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM archived_media")

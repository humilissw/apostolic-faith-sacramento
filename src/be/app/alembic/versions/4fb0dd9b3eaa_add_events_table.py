"""add events table

Revision ID: 4fb0dd9b3eaa
Revises: 336acd53a355
Create Date: 2026-07-31 15:31:42.007528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '4fb0dd9b3eaa'
down_revision: Union[str, Sequence[str], None] = '336acd53a355'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('events',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=4000), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('events')

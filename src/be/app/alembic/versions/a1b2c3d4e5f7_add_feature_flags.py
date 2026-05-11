"""add feature_flags table

Revision ID: a1b2c3d4e5f7
Revises: h1i2j3k4l5m6
Create Date: 2026-05-08

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, Sequence[str], None] = "h1i2j3k4l5m6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=100), unique=True, nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
    )

    # Seed default feature flags
    op.execute(
        """
        INSERT INTO feature_flags (id, name, description, is_enabled, created_on, updated_on)
        VALUES
        (UUID(), 'enable_home', 'Show the home page', 1, NOW(), NULL),
        (UUID(), 'enable_doctrines', 'Show the doctrines page', 1, NOW(), NULL),
        (UUID(), 'enable_contact', 'Show the contact page', 1, NOW(), NULL),
        (UUID(), 'enable_media', 'Show the media page', 1, NOW(), NULL),
        (UUID(), 'enable_donate', 'Show the donate page', 1, NOW(), NULL),
        (UUID(), 'enable_sermon', 'Show the sermon page', 1, NOW(), NULL),
        (UUID(), 'enable_live_service', 'Show the live service page', 1, NOW(), NULL),
        (UUID(), 'enable_video_uploads', 'Show the video uploads page', 1, NOW(), NULL),
        (UUID(), 'enable_scheduler_calendar', 'Show the scheduler calendar', 1, NOW(), NULL),
        (UUID(), 'enable_scheduler_admin', 'Show the scheduler admin page', 1, NOW(), NULL),
        (UUID(), 'enable_my_scheduler', 'Show the my scheduler page', 1, NOW(), NULL),
        (UUID(), 'enable_users_admin', 'Show the users admin page', 1, NOW(), NULL),
        (UUID(), 'enable_video_uploads_admin', 'Show the video uploads admin page', 1, NOW(), NULL),
        (UUID(), 'enable_integrations', 'Show the integrations page', 1, NOW(), NULL)
        ON DUPLICATE KEY UPDATE name = name
        """
    )


def downgrade() -> None:
    op.drop_table("feature_flags")

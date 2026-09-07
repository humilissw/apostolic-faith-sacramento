"""seed all remaining known feature flags

Idempotently inserts every flag from KNOWN_FEATURE_FLAGS that is missing,
including enable_events, enable_events_admin and enable_admin_password_reset
which were added to the service without a matching seed migration. Existing
rows are left untouched so admin-toggled values survive.

Revision ID: q5r6s7t8u9v0
Revises: 4fb0dd9b3eaa
Create Date: 2026-09-06

"""

from typing import Sequence, Union

from alembic import op

revision: str = "q5r6s7t8u9v0"
down_revision: Union[str, Sequence[str], None] = "4fb0dd9b3eaa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mirrors app.services.feature_flag_service.KNOWN_FEATURE_FLAGS
KNOWN_FLAGS = [
    ("enable_home", "Show the home page"),
    ("enable_doctrines", "Show the doctrines page"),
    ("enable_contact", "Show the contact page"),
    ("enable_media", "Show the media page"),
    ("enable_donate", "Show the donate page"),
    ("enable_sermon", "Show the sermon page (external YouTube)"),
    ("enable_live_service", "Show the live service page"),
    ("enable_video_uploads", "Show the video uploads page"),
    ("enable_scheduler_calendar", "Show the scheduler calendar"),
    ("enable_scheduler_admin", "Show the scheduler admin page"),
    ("enable_my_scheduler", "Show the my scheduler page"),
    ("enable_users_admin", "Show the users admin page"),
    ("enable_video_uploads_admin", "Show the video uploads admin page"),
    ("enable_integrations", "Show the integrations page"),
    ("enable_flags_admin", "Show the feature flags admin page"),
    ("enable_events", "Show the events page"),
    ("enable_events_admin", "Show the events admin page"),
    (
        "enable_admin_password_reset",
        "Allow administrators to send password reset emails for any user",
    ),
]


def upgrade() -> None:
    for name, desc in KNOWN_FLAGS:
        # Insert-if-missing only: ON DUPLICATE KEY on the unique `name` column
        # must NOT overwrite is_enabled (admins may have toggled flags off).
        op.execute(
            "INSERT INTO feature_flags (id, name, description, is_enabled, created_on, updated_on) "
            f"VALUES (UUID(), '{name}', '{desc}', 1, NOW(), NULL) "
            "ON DUPLICATE KEY UPDATE name = name"
        )


def downgrade() -> None:
    pass

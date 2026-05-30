"""enable all feature flags

Revision ID: m1n2o3p4q5r6
Revises: a1b2c3d4e5f7
Create Date: 2026-05-08

"""

from typing import Sequence, Union


from alembic import op

revision: str = "m1n2o3p4q5r6"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

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
]


# def _flag_uuid(name: str) -> str:
#     """Deterministic UUID from flag name for idempotent migrations."""
#     return str(uuid_mod.UUID(int=hash(name)))


def upgrade() -> None:
    for name, desc in KNOWN_FLAGS:
        # fid = _flag_uuid(name)
        op.execute(
            f"""
            INSERT INTO feature_flags (id, name, description, is_enabled, created_on, updated_on)
            VALUES ('UUID()', '{name}', '{desc}', 1, NOW(), NULL)
            ON DUPLICATE KEY UPDATE is_enabled = 1, updated_on = NOW()
            """
        )


def downgrade() -> None:
    pass

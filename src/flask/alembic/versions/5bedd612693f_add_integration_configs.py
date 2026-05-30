"""add_integration_configs

Revision ID: 5bedd612693f
Revises: e7562edf08a2
Create Date: 2026-05-03 13:13:02.228641

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5bedd612693f"
down_revision: Union[str, Sequence[str], None] = "e7562edf08a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

KNOWN_INTEGRATIONS = [
    {"type": "stripe", "display_name": "Stripe Payments", "icon": "CreditCard"},
    {"type": "twilio", "display_name": "Twilio SMS", "icon": "MessageSquare"},
    {"type": "sendgrid", "display_name": "SendGrid Email", "icon": "Mail"},
    {"type": "youtube", "display_name": "YouTube", "icon": "Youtube"},
    {"type": "facebook", "display_name": "Facebook", "icon": "Facebook"},
    {"type": "spotify", "display_name": "Spotify Music", "icon": "Music"},
]


def upgrade() -> None:
    """Create integration_configs table with pre-seeded data."""
    op.create_table(
        "integration_configs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column("type", sa.String(length=50), unique=True, nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("icon", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("config_json", sa.String(length=4000), nullable=True),
        sa.Column("cred_key_id", sa.String(length=100), nullable=True),
        sa.Column("cred_encrypted_iv", sa.String(length=255), nullable=True),
        sa.Column("cred_encrypted_blob", sa.String(length=4000), nullable=True),
    )

    # Pre-seed known integration types
    conn = op.get_bind()
    for integration in KNOWN_INTEGRATIONS:
        conn.execute(
            sa.text(
                "INSERT INTO integration_configs "
                "(id, created_on, updated_on, type, display_name, icon, "
                "enabled, status, last_synced_at, config_json, cred_key_id, "
                "cred_encrypted_iv, cred_encrypted_blob) "
                "VALUES (UUID(), NOW(), NOW(), :type, :display_name, :icon, "
                "0, 'disconnected', NULL, NULL, NULL, NULL, NULL)"
            ).bindparams(**integration)
        )


def downgrade() -> None:
    """Drop integration_configs table."""
    op.drop_table("integration_configs")

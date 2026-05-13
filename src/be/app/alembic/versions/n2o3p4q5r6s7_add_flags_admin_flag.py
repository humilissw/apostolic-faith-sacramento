"""add flags_admin feature flag

Revision ID: n2o3p4q5r6s7
Revises: m1n2o3p4q5r6
Create Date: 2026-05-11

"""

from typing import Sequence, Union


from alembic import op

revision: str = "n2o3p4q5r6s7"
down_revision: Union[str, Sequence[str], None] = "m1n2o3p4q5r6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO feature_flags (id, name, description, is_enabled, created_on, updated_on)
        VALUES (UUID(), 'enable_flags_admin', 'Show the feature flags admin page', 1, NOW(), NULL)
        ON DUPLICATE KEY UPDATE is_enabled = 1, updated_on = NOW()
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM feature_flags WHERE name = 'enable_flags_admin'")

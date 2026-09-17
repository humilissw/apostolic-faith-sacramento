"""append new media rows from AFC Sacramento YouTube channel

Revision ID: f271c210a6fe
Revises: s7t8u9v0w1x2
Create Date: 2026-09-16 05:20:45.816627

Incremental data migration (generated with --append): contains ONLY videos from
the latest extraction that earlier media seed/append migrations do not already
cover. Previously generated migrations are untouched. Rows are idempotent —
ids are UUID5 of the YouTube video id and inserts use ON DUPLICATE KEY UPDATE.
"""

from typing import Sequence, Union


from alembic import op

revision: str = "f271c210a6fe"
down_revision: Union[str, Sequence[str], None] = "s7t8u9v0w1x2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (id, name, description, owner_id, uploaded_on) — only NEW YouTube videos.
MEDIA_ROWS = [
    (
        "728d4470-870e-525e-a821-32556ecca72e",
        "Voice Recognition - Wisdom from the Spirit — Rev. Mark Worthington • 1 Corinthians 2: 6-16",
        "9/13/2026 — 11:00 am Sunday morning service - Voice Recognition - Wisdom from the Spirit — Rev. Mark Worthington • 1 Corinthians 2: 6-16\n\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org; email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-09-14 00:00:00",
    ),  # youtube:32556ecca72e
    (
        "6c2af8a5-73c4-599d-8af2-6888b623099d",
        "I have something to tell you — Bro. Sorin Filimon • Luke 7:40",
        "9/6/2026 — 11:00 am Sunday morning service - I have something to tell you — Bro. Sorin Filimon • Luke 7:40\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org; email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-09-12 00:00:00",
    ),  # youtube:6888b623099d
    (
        "08637bae-d7fa-5ecf-894f-a1fc780f1b12",
        "Numbering Our Days — Rev. Mark Worthington • Psalm 90:1-17",
        "8/30/2026 — 11:00 am Sunday morning service -  Numbering Our Days — Rev. Mark Worthington • Psalm 90:1-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-09-04 00:00:00",
    ),  # youtube:a1fc780f1b12
    (
        "da7844de-4108-57b3-97f0-2e21daf4d213",
        "Grow! Grow! Grow! — Rev. Pete Sferle • 2 Peter 3:15-18",
        "8/23/2026 — 11:00 am Sunday morning service - Grow! Grow! Grow! — Rev. Pete Sferle • 2 Peter 3:15-18 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org; email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-27 00:00:00",
    ),  # youtube:2e21daf4d213
]


def _insert_sql(row: tuple) -> str:
    media_id, name, description, owner_id, ts = row
    desc_literal = "NULL" if description is None else f"'{description}'"
    return (
        "INSERT INTO media (id, name, description, owner_id, uploaded_on, created_on, updated_on) "
        f"VALUES ('{media_id}', '{name}', {desc_literal}, '{owner_id}', '{ts}', '{ts}', '{ts}') "
        "ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description), "
        "updated_on = VALUES(updated_on)"
    )


def upgrade() -> None:
    for row in MEDIA_ROWS:
        op.execute(_insert_sql(row))


def downgrade() -> None:
    ids = ", ".join(f"'{row[0]}'" for row in MEDIA_ROWS)
    op.execute(f"DELETE FROM media WHERE id IN ({ids})")

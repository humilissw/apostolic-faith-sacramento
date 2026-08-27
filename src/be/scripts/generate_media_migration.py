#!/usr/bin/env python3
"""Generate an Alembic data migration seeding the ``media`` table from YouTube.

ELT step 2 (TRANSFORM + LOAD). Reads the raw extraction produced by
extract_youtube_services.py and emits a single Alembic revision that inserts one
``media`` row per YouTube video:

    media.id          -> deterministic UUID5 of the YouTube video id
    media.name        -> YouTube title
    media.description -> YouTube description (nullable; must fit in 4000 chars)
    media.owner_id    -> --owner-id (default: all-zeros UUID used as the
        server_default in migration a1b2c3d4e5f6)
    media.uploaded_on -> YouTube upload date (upload_date, YYYYMMDD) at midnight
    media.created_on  -> same as uploaded_on (when the video went public)
    media.updated_on  -> same as uploaded_on

Idempotency: ids are deterministic (uuid5 of the video id) and each row is
inserted with ``ON DUPLICATE KEY UPDATE name = VALUES(name), updated_on =
VALUES(updated_on)``, so re-running after a fresh extraction only updates changed
titles instead of failing or duplicating.

The generated revision's down_revision is auto-detected from the current head in
app/alembic/versions/, so it always chains onto whatever is latest.

Usage:
    python3 scripts/generate_media_migration.py
    python3 scripts/generate_media_migration.py --data data/youtube_services_raw.json
    python3 scripts/generate_media_migration.py --owner-id <uuid> --dry-run

After generating, apply with:  alembic upgrade head
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_BE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA = REPO_BE_DIR / "data" / "youtube_services_raw.json"
VERSIONS_DIR = REPO_BE_DIR / "app" / "alembic" / "versions"
DEFAULT_OWNER_ID = "00000000-0000-0000-0000-000000000000"

# Stable namespaced UUID so re-extractions of the same video map to the same row.
MEDIA_NAMESPACE = uuid.UUID("6ba7b812-9dad-11d1-80b4-00c04fd430c8")  # NAMESPACE_URL


def load_raw_data(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: could not read raw extraction {path}: {exc}")
    videos = payload.get("videos", [])
    if not videos:
        sys.exit(f"error: no videos found in {path}; run extract_youtube_services.py first")
    return videos


def _revision_files(versions_dir: Path):
    """Yield migration files, excluding the seed migration this script manages.

    Excluding it keeps `current_head`/revision scanning stable across
    first-generation and in-place regeneration (otherwise a regenerated file
    would become its own down_revision).
    """
    for f in sorted(versions_dir.glob("*.py")):
        if f.name.endswith("_seed_media_from_youtube.py"):
            continue
        yield f


def existing_revisions(versions_dir: Path) -> set[str]:
    revs = set()
    for f in _revision_files(versions_dir):
        m = re.search(r'^revision: str = "([^"]+)"', f.read_text(), re.M)
        if m:
            revs.add(m.group(1))
    return revs


def current_head(versions_dir: Path) -> str | None:
    """Find the alembic head by scanning revision/down_revision pairs."""
    revisions: dict[str, str | None] = {}
    for f in _revision_files(versions_dir):
        text = f.read_text()
        rev = re.search(r'^revision: str = "([^"]+)"', text, re.M)
        down = re.search(r'^down_revision: [^=]*= ("[^"]+"|None)', text, re.M)
        if rev:
            revisions[rev.group(1)] = (
                down.group(1).strip('"') if down and down.group(1) != "None" else None
            )
    children = {d for d in revisions.values() if d}
    heads = [r for r in revisions if r not in children]
    if len(heads) != 1:
        sys.exit(f"error: expected exactly one alembic head, found: {heads}")
    return heads[0]


def new_revision_id(versions_dir: Path) -> str:
    """Generate a 12-hex-char revision id that does not collide with existing ones."""
    taken = existing_revisions(versions_dir)
    while True:
        rev = secrets.token_hex(6)
        if rev not in taken:
            return rev


def sql_str(value: str) -> str:
    """Escape a string for embedding inside a MySQL/MariaDB single-quoted literal."""
    return value.replace("\\", "\\\\").replace("'", "''")


def build_row(video: dict, owner_id: str) -> tuple[str, str, str | None, str, str]:
    """Return (id, name_sql_literal_body, description_sql_literal_body, owner_id, timestamp)."""
    video_id = video["id"]
    upload_date = video.get("upload_date") or ""
    if not re.fullmatch(r"\d{8}", upload_date):
        sys.exit(f"error: video {video_id} has invalid upload_date {upload_date!r}")
    ts = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]} 00:00:00"

    description = (video.get("description") or "").strip() or None
    if description is not None and len(description) > 4000:
        sys.exit(f"error: video {video_id} description exceeds 4000 chars ({len(description)})")

    return (
        str(uuid.uuid5(MEDIA_NAMESPACE, f"youtube:{video_id}")),
        sql_str(video["title"]),
        sql_str(description) if description is not None else None,
        owner_id,
        ts,
    )


def render_rows(rows: list[tuple[str, str, str | None, str, str]]) -> str:
    """Render the MEDIA_ROWS list body as Python source (repr() per value)."""
    lines = []
    for media_id, name_sql, desc_sql, owner_id, ts in rows:
        # repr() yields a valid Python string literal for each value. The name and
        # description are already SQL-escaped so they are safe to splice into the
        # SQL at runtime.
        lines.append(
            f"    ({media_id!r}, {name_sql!r}, {desc_sql!r}, {owner_id!r}, {ts!r}),  "
            f"# youtube:{media_id[-12:]}"
        )
    return "\n".join(lines)


# The function bodies below contain real Python f-strings with braces, so they are
# kept verbatim and assembled by plain concatenation (never passed through .format()).
HEADER = '''"""seed media table from AFC Sacramento YouTube channel

Revision ID: {revision}
Revises: {down_revision_display}
Create Date: {create_date}

Data migration: one row per video on the channel (extracted via
scripts/extract_youtube_services.py). Rows are idempotent — ids are UUID5 of the
YouTube video id and inserts use ON DUPLICATE KEY UPDATE, so re-running after a
fresh extraction only updates changed titles/descriptions.
"""

from typing import Sequence, Union


from alembic import op

revision: str = "{revision}"
down_revision: Union[str, Sequence[str], None] = {down_revision_repr}
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (id, name, description, owner_id, uploaded_on) — one tuple per YouTube video.
MEDIA_ROWS = [
'''

FOOTER = """
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
"""


def build_content(revision: str, down_revision: str | None, rows_block: str) -> str:
    header = HEADER.format(
        revision=revision,
        down_revision_display=down_revision if down_revision is not None else "(base)",
        down_revision_repr=f'"{down_revision}"' if down_revision is not None else "None",
        create_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f"),
    )
    return header + rows_block + FOOTER


def find_existing_seed_migration(versions_dir: Path) -> tuple[Path, str] | None:
    """Locate a previously generated seed migration so regeneration replaces it
    in place (same revision id + filename) instead of stacking a new revision."""
    for f in sorted(versions_dir.glob("*_seed_media_from_youtube.py")):
        m = re.search(r'^revision: str = "([^"]+)"', f.read_text(), re.M)
        if m:
            return f, m.group(1)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="raw extraction JSON")
    parser.add_argument("--owner-id", default=DEFAULT_OWNER_ID, help="owner_id UUID for all rows")
    parser.add_argument(
        "--out", type=Path, default=None, help="output migration path (default: auto in versions/)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print the migration to stdout instead of writing it"
    )
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-fA-F-]{36}", args.owner_id):
        sys.exit(f"error: --owner-id must be a UUID, got {args.owner_id!r}")

    videos = load_raw_data(args.data)
    head = current_head(VERSIONS_DIR)
    rows = [build_row(v, args.owner_id) for v in videos]

    existing = None if args.out or args.dry_run else find_existing_seed_migration(VERSIONS_DIR)
    if existing:
        out_path, revision = existing
        print(f"regenerating existing migration in place: {out_path.name}")
    else:
        revision = new_revision_id(VERSIONS_DIR)
        out_path = args.out or VERSIONS_DIR / f"{revision}_seed_media_from_youtube.py"

    content = build_content(revision, head, render_rows(rows))

    if args.dry_run:
        print(content)
        return

    out_path.write_text(content)
    print(f"wrote {len(rows)} media rows to {out_path}")
    print(f"  down_revision: {head}")
    print("apply with: alembic upgrade head")


if __name__ == "__main__":
    main()

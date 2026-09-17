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

Incremental mode (append-only):
    python3 scripts/generate_media_migration.py --append

    With --append the script NEVER rewrites previously generated seed
    migrations. It reads every row already covered by existing media seed
    migrations (any *_seed_media_from_youtube.py in versions/), compares
    against the raw extraction, and:
    * if there are new videos -> emits ONE NEW revision chained on the
        current head containing ONLY the not-yet-seeded rows;
    * if every video is already covered -> writes nothing at all.
    Without --append the legacy behaviour is kept: the single seed migration
    is regenerated in place with ALL rows.

After generating, apply with:  alembic upgrade head
"""

from __future__ import annotations

import argparse
import ast
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


def _revision_files(versions_dir: Path, exclude_managed: bool = False):
    """Yield migration files.

    Legacy (regenerate-in-place) mode passes exclude_managed=True so the seed
    migration being rewritten is skipped — otherwise a regenerated file would
    become its own down_revision when the seed happens to be the head. Append
    mode scans everything: every existing revision (seeds and appends alike) is
    committed history that the new incremental revision must chain onto.
    """
    for f in sorted(versions_dir.glob("*.py")):
        if exclude_managed and _is_managed_migration(f):
            continue
        yield f


def _is_managed_migration(f: Path) -> bool:
    return f.name.endswith("_seed_media_from_youtube.py") or f.name.endswith(
        "_append_media_from_youtube.py"
    )


def existing_revisions(versions_dir: Path, exclude_managed: bool = False) -> set[str]:
    revs = set()
    for f in _revision_files(versions_dir, exclude_managed):
        m = re.search(r'^revision: str = "([^"]+)"', f.read_text(), re.M)
        if m:
            revs.add(m.group(1))
    return revs


def current_head(versions_dir: Path, exclude_managed: bool = False) -> str | None:
    """Find the alembic head by scanning revision/down_revision pairs."""
    revisions: dict[str, str | None] = {}
    for f in _revision_files(versions_dir, exclude_managed):
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


def new_revision_id(versions_dir: Path, exclude_managed: bool = False) -> str:
    """Generate a 12-hex-char revision id that does not collide with existing ones."""
    taken = existing_revisions(versions_dir, exclude_managed)
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

# Variant used by --append: an incremental revision containing ONLY videos that
# no earlier media seed/append migration covers. Previously generated
# migrations are never rewritten.
APPEND_HEADER = '''"""append new media rows from AFC Sacramento YouTube channel

Revision ID: {revision}
Revises: {down_revision_display}
Create Date: {create_date}

Incremental data migration (generated with --append): contains ONLY videos from
the latest extraction that earlier media seed/append migrations do not already
cover. Previously generated migrations are untouched. Rows are idempotent —
ids are UUID5 of the YouTube video id and inserts use ON DUPLICATE KEY UPDATE.
"""

from typing import Sequence, Union


from alembic import op

revision: str = "{revision}"
down_revision: Union[str, Sequence[str], None] = {down_revision_repr}
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (id, name, description, owner_id, uploaded_on) — only NEW YouTube videos.
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


def build_content(
    revision: str, down_revision: str | None, rows_block: str, header: str = HEADER
) -> str:
    header = header.format(
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


def find_append_migrations(versions_dir: Path) -> list[Path]:
    """Append revisions previously emitted by --append (if any)."""
    return sorted(versions_dir.glob("*_append_media_from_youtube.py"))


def covered_media_ids(versions_dir: Path) -> set[str]:
    """Media row ids already covered by previously generated migrations.

    Parses the MEDIA_ROWS list literal (via ast — never executes migration
    code) out of every seed/append media migration in versions/, so --append
    knows exactly which videos are already seeded.
    """
    covered: set[str] = set()
    for f in sorted(versions_dir.glob("*_media_from_youtube.py")):
        if not (_is_managed_migration(f)):
            continue
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError as exc:
            sys.exit(f"error: could not parse existing migration {f}: {exc}")
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "MEDIA_ROWS" for t in node.targets)
                and isinstance(node.value, (ast.List, ast.Tuple))
            ):
                for item in node.value.elts:
                    if isinstance(item, (ast.Tuple, ast.List)) and item.elts:
                        first = item.elts[0]
                        if isinstance(first, ast.Constant) and isinstance(first.value, str):
                            covered.add(first.value)
    return covered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="raw extraction JSON")
    parser.add_argument("--owner-id", default=DEFAULT_OWNER_ID, help="owner_id UUID for all rows")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output migration path (default: auto in versions/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the migration to stdout instead of writing it",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="incremental mode: emit a NEW revision with only videos not yet "
        "covered by existing media seed/append migrations; never rewrite them",
    )
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-fA-F-]{36}", args.owner_id):
        sys.exit(f"error: --owner-id must be a UUID, got {args.owner_id!r}")

    videos = load_raw_data(args.data)

    if args.append:
        # Incremental mode: seed migrations become history — chain onto the real
        # head (which may itself be a previous append) and skip covered videos.
        head = current_head(VERSIONS_DIR)
        covered = covered_media_ids(VERSIONS_DIR)
        rows = []
        seen_new: set[str] = set()
        for v in videos:
            row = build_row(v, args.owner_id)
            if row[0] in covered or row[0] in seen_new:
                continue
            seen_new.add(row[0])
            rows.append(row)

        print(
            f"{len(videos)} videos in extraction; {len(videos) - len(rows)} already "
            f"covered by existing migrations; {len(rows)} new"
        )
        if not rows:
            print("nothing to append — every video is already seeded. No migration written.")
            return

        revision = new_revision_id(VERSIONS_DIR)
        out_path = args.out or VERSIONS_DIR / f"{revision}_append_media_from_youtube.py"
        content = build_content(revision, head, render_rows(rows), header=APPEND_HEADER)

        if args.dry_run:
            print(content)
            return

        out_path.write_text(content)
        print(f"appended {len(rows)} new media rows to {out_path}")
        print(f"  down_revision: {head}")
        print("apply with: alembic upgrade head")
        return

    appends = find_append_migrations(VERSIONS_DIR)
    if appends:
        sys.exit(
            "error: append migrations already exist "
            f"({', '.join(p.name for p in appends)}). The seed migration is no longer "
            "the tip of the chain — regenerate-in-place would corrupt it. Use "
            "--append to add new videos incrementally instead."
        )

    head = current_head(VERSIONS_DIR, exclude_managed=True)
    rows = [build_row(v, args.owner_id) for v in videos]

    existing = None if args.out or args.dry_run else find_existing_seed_migration(VERSIONS_DIR)
    if existing:
        out_path, revision = existing
        print(f"regenerating existing migration in place: {out_path.name}")
    else:
        revision = new_revision_id(VERSIONS_DIR, exclude_managed=True)
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

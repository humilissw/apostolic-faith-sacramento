#!/usr/bin/env python3
"""Generate an Alembic data migration seeding ``video_uploads`` from YouTube.

ELT step 3 (TRANSFORM + LOAD). Reads the same raw extraction consumed by
generate_media_migration.py (data/youtube_services_raw.json) and emits a single
Alembic revision that inserts one ``video_uploads`` row per YouTube video that
carries a scripture reference:

    video_uploads.id                     -> deterministic UUID5 of the YouTube
                                            video id (same value as the matching
                                            media row, so the two stay in lockstep)
    video_uploads.upload_location        -> YouTube watch URL (video["url"])
    video_uploads.upload_name            -> sermon title (parsed from the
                                            description's first line; falls back
                                            to the JSON "title" field)
    video_uploads.speaker_name           -> speaker (parsed; NULL when absent)
    video_uploads.reference_text         -> scripture reference (parsed; <=50 chars)
    video_uploads.description            -> verbatim YouTube description (all lines)
    video_uploads.owner_id               -> --owner-id (default all-zeros UUID,
                                            same server_default as media)
    video_uploads.media_association_date -> YouTube upload date (upload_date,
                                            YYYYMMDD) at midnight UTC
    video_uploads.created_on             -> same as media_association_date
    video_uploads.updated_on             -> same as media_association_date

Videos whose description/title contains NO scripture reference are skipped
(per the task spec). "Scripture reference" = a Bible book + chapter[:verse]
token, or the word "Scripture" introducing one.

Parsing rules (from the data owner):
    * The description's FIRST line holds ``[title - speaker • reference_text]``.
        The dash separates title from speaker; the bullet ("•") separates speaker
        from reference. Order varies, so each field is located by its shape rather
        than strict position:
        - reference = a book + chapter[:verse] run (the "•" segment, or the text
            after the word "Scripture"); multiple references are joined with "; ".
        - speaker   = an honorific-prefixed name (Rev./Bro./Sis./etc.); if a
            segment contains ":" it is scripture, never a speaker.
        - title     = what remains once the date/time header, reference(s) and
            speaker are removed.
    * Common case first: parse the description's first line. If that yields no
        reference (or an unusable title), fall back to the JSON "title" field.

Idempotency: ids are deterministic (uuid5 of the video id) and each row is
inserted with ``ON DUPLICATE KEY UPDATE`` over every derived column, so
re-running after a fresh extraction only updates changed values instead of
failing or duplicating.

The generated revision's down_revision is auto-detected from the current head
in app/alembic/versions/, so it always chains onto whatever is latest (i.e. on
top of the media seed revision).

Usage:
    python3 scripts/generate_video_uploads_migration.py
    python3 scripts/generate_video_uploads_migration.py --data data/youtube_services_raw.json
    python3 scripts/generate_video_uploads_migration.py --owner-id <uuid> --dry-run

After generating, apply with:  alembic upgrade head
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_BE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA = REPO_BE_DIR / "data" / "youtube_services_raw.json"
VERSIONS_DIR = REPO_BE_DIR / "app" / "alembic" / "versions"
DEFAULT_OWNER_ID = "00000000-0000-0000-0000-000000000000"

# Same namespaced UUID as the media seed so a given video maps to the same id in
# both tables (keeps the 1:1 correspondence explicit and ids stable).
MEDIA_NAMESPACE = uuid.UUID("6ba7b812-9dad-11d1-80b4-00c04fd430c8")  # NAMESPACE_URL

MAX_REFERENCE_LEN = 50  # video_uploads.reference_text max_length


# ---------------------------------------------------------------------------
# Parsing (self-contained; no project imports so the script runs anywhere)
# ---------------------------------------------------------------------------

# Bible book names. Multi-word books (e.g. "1 Samuel", "Song of Solomon") must stay
# intact — a flat whitespace split would leak bare "1"/"2"/"3"/"of" tokens that then
# false-match on dates like "2023 11:00". Order is irrelevant; the regex sorts by length.
BOOKS = [
    # Old Testament
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Psalm",
    "Proverbs",
    "Prov",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Isiah",
    "Jeremiah",
    "Lamentations",
    "Lam",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    # New Testament
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
    "Rev",
]
_BOOK_ALT = "|".join(re.escape(w) for w in sorted(set(BOOKS), key=len, reverse=True))

# Lower-cased book words (single-word books + last words of multi-word books) used to
# trim a book name that bled into the end of an over-captured speaker name.
_BOOK_WORDS = {w.lower() for w in BOOKS} | {
    "samuel",
    "kings",
    "chronicles",
    "corinthians",
    "thessalonians",
    "timothy",
    "peter",
    "john",
    "solomon",
}

# Last words of multi-word books, so an adjacent second book can be matched even when
# its numeric prefix was consumed by the previous book's chapter (e.g. "Revelation 2
# Thessalonians 2:1-12" -> anchor "Revelation 2", continuation "Thessalonians 2:1-12").
_LAST_WORDS = {
    "Samuel",
    "Kings",
    "Chronicles",
    "Corinthians",
    "Thessalonians",
    "Timothy",
    "Peter",
    "John",
    "Solomon",
}
_CONT_BOOK_ALT = "|".join(
    re.escape(w) for w in sorted(set(BOOKS) | _LAST_WORDS, key=len, reverse=True)
)

# Numeric tail after a book name. Handles the malformed variants present in the data:
#   "8:1-2"  (chapter:verse-range), "12-2" (chapter-range, missing colon),
#   "40:27:31" (two verse groups), "23" (chapter only). A space before the colon
#   ("Joshua 4 :19") is tolerated.
_TAIL = (
    r"\d{1,3}(?:\s*[-–]\s*\d{1,3})?"
    r"(?:\s*:\s*[1-9]\d{0,2}(?:\s*[-–]\s*\d{1,3})?)?"
    r"(?:\s*:\s*[1-9]\d{0,2}(?:\s*[-–]\s*\d{1,3})?)?"
)

# Anchor: optional "St " + optional 1/2/3 prefix + book name + numeric tail.
_ANCHOR = r"(?:St\s+)?(?:(?:1|2|3)\s+)?(?:%s)\.?\s+%s" % (_BOOK_ALT, _TAIL)
# Continuation (repeated): either a separator (optionally with the words Scripture/Reading
# and/or a dash) followed by another book-ref or a bare chapter:verse, OR an adjacent
# book name + tail with no separator. This collapses "A › Scripture B", "A; B" and
# "Revelation 2 Thessalonians 2:1-12" into one run while stopping at title/speaker words.
_CONT = (
    r"(?:\s*[;,›»–—]?\s*(?:(?:Scripture|Reading)\b\s*)*\s*:? ?(?:%s\.?\s+%s|"
    r"\d{1,3}:\s*[1-9]\d{0,2}(?:\s*[-–]\s*\d{1,3})?))"
    r"|(?:\s+(?:%s)\.?\s+%s)"
) % (_BOOK_ALT, _TAIL, _CONT_BOOK_ALT, _TAIL)
REF_RUN_RE = re.compile(_ANCHOR + "(?:" + _CONT + ")*", re.IGNORECASE)

# Honorific-prefixed speaker name. Handles "Rev.", "Rev .", "Rev.Pete", "Brother", etc.
SPEAKER_RE = re.compile(
    r"(?:Brother|Sister|Rev|Bro|Sis|Deacon|Dr)\b[.\s]*([A-Z][\w.'']*(?:\s+[A-Z][\w.'']*){0,3})"
)

FOOTER_MARKERS = [
    "Trinity Apostolic",
    "For more information",
    "CCLI",
    "afcsacramento.org",
    "pete@sferle.com",
]


def norm(s: str | None) -> str:
    """Normalize unicode, collapse NBSP/thin spaces, squeeze whitespace."""
    s = unicodedata.normalize("NFKC", s or "")
    for ch in "\u00a0\u2009\u200a":
        s = s.replace(ch, " ")
    return re.sub(r"\s+", " ", s).strip()


def first_line(desc: str | None) -> str:
    return norm((desc or "").split("\n")[0])


def strip_footer(s: str) -> str:
    """Cut the church contact/CCLI footer that is sometimes inlined on line 1."""
    for marker in FOOTER_MARKERS:
        i = s.find(marker)
        if i != -1:
            s = s[:i]
    return norm(s).strip(" -–—•›»")


def find_refs(seg: str) -> list[str]:
    """All scripture reference runs in seg, as matched (raw, whitespace-collapsed)."""
    out: list[str] = []
    for m in REF_RUN_RE.finditer(seg):
        r = norm(m.group(0))
        if r:
            out.append(r)
    return out


def clean_run(raw: str) -> str:
    """Clean one matched reference run into the reference_text value.

    Normalizes the arrow/guillemet separators to "; ", drops the words "Scripture"
    and "Reading", and collapses duplicated separators. Intra-reference hyphens
    (verse ranges like "12-2") are left untouched.
    """
    s = norm(raw)
    s = re.sub(r"\s*[›»]\s*", "; ", s)  # arrows/guillemets -> '; '
    s = re.sub(r"\b(?:Scripture|Reading)\b\s*:? ?", "", s, flags=re.I)  # drop the words
    s = re.sub(r";\s*[-–—]\s*", "; ", s)  # dangling dash after a separator
    s = re.sub(r"[-–—]\s*;", ";", s)
    s = norm(s)
    s = re.sub(r"(?:;\s*){2,}", "; ", s)  # collapse doubled separators
    return s.strip("; -–—•›»")


def find_speaker(seg: str) -> str | None:
    """The honorific-prefixed speaker name, or None. A segment with ':' is never a speaker."""
    matches = list(SPEAKER_RE.finditer(seg))
    if not matches:
        # Fallback: trailing capitalized 2-3 word name after a dash (no honorific).
        m = re.search(r"[—–-]\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*$", norm(seg))
        return _trim_speaker(norm(m.group(1))) if m else None
    return _trim_speaker(norm(matches[-1].group(0)))


def _trim_speaker(name: str) -> str | None:
    """Drop trailing book-name words the speaker regex over-captured.

    e.g. "Bro. Sorin Filimon Romans" -> "Bro. Sorin Filimon" (the reference's book
    name bled into the 3-word name capture). A leading numeric prefix belonging to
    a multi-word book ("2 Peter") is trimmed with it.
    """
    words = name.split()
    while len(words) > 2 and words[-1].lower() in _BOOK_WORDS:
        words.pop()
        # if the new last word is a numeric prefix of a multi-word book, drop it too
        if re.fullmatch(r"[123]", words[-1]) and len(words) >= 2:
            words.pop()
    return " ".join(words).strip() or None


HEADER_WORDS = {
    "morning",
    "evening",
    "afternoon",
    "am",
    "pm",
    "service",
    "services",
    "devotional",
    "devotionals",
    "meeting",
    "meetings",
    "youth",
    "children's",
    "child",
    "special",
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "jan",
    "feb",
    "mar",
    "apr",
    "jun",
    "jul",
    "aug",
    "sep",
    "sept",
    "oct",
    "nov",
    "dec",
}

# A token that is a date/time (not just a bare number), so titles like "12 Days of
# Christmas" are not mistaken for a header.
_DATE_TIME_TOKEN = re.compile(r"\d{1,2}[./]\d|\d{1,2}:\d{2}|\d{4}")


def _is_header_token(tok: str) -> bool:
    t = tok.lower().strip(".,;:—–-•›»")
    if not t:
        return True  # separator-only token
    if re.fullmatch(r"[\d:./,]+", t):
        return True
    return t in HEADER_WORDS


def strip_header(s: str) -> str:
    """Strip a leading service header (date/time/weekday + service words).

    Walks the maximal leading run of header tokens and removes it ONLY if that run
    contains a real date/time token. This preserves titles that merely start with a
    weekday or month name ("Palm Sunday", "Easter Sunday", "Thanksgiving") while
    removing "8/16/2026 — 5:00 pm Sunday evening service - " and the like.
    """
    s = norm(s)
    tokens = re.findall(r"\S+", s)
    i, has_date_time = 0, False
    while i < len(tokens):
        low = tokens[i].lower().strip(".,;:—–-•›»")
        if re.fullmatch(r"[\d:./,]+", low) and _DATE_TIME_TOKEN.search(low):
            has_date_time = True
        if _is_header_token(tokens[i]):
            i += 1
        else:
            break
    if i > 0 and has_date_time:
        return norm(" ".join(tokens[i:]))
    return s


def clean_title(s: str) -> str:
    s = strip_header(norm(s))
    s = re.sub(r"[\s•›»]+", " ", s)  # bullets/arrows/extra spaces -> single space
    s = re.sub(r"\s*[-–—]+\s*", " — ", s)  # dashes -> a single spaced em dash
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip(" -–—•›».,")


def _derive(source: str, refs_raw: list[str], speaker: str | None) -> str:
    """Title by removal: strip the raw reference run(s), the speaker, then clean up."""
    t = source
    for r in refs_raw:
        t = t.replace(r, " ")
    if speaker:
        t = t.replace(speaker, " ")
    return clean_title(strip_footer(t))


def parse_line(text: str) -> dict | None:
    """Parse a ``[title - speaker • reference]`` line. Returns fields or None (no ref)."""
    seg = strip_footer(norm(text))
    if not seg:
        return None
    refs_raw = find_refs(seg)
    if not refs_raw and re.search(r"\bScripture\b", seg, re.IGNORECASE):
        # User rule: the word "Scripture" introduces the reference that follows.
        m = re.search(r"\bScripture\b\s*:? ?(.+?)(?:[•›»]|$)", seg, re.IGNORECASE)
        if m:
            refs_raw = [norm(m.group(1)).strip(" -–—")]
    if not refs_raw:
        return None
    ref = "; ".join(clean_run(r) for r in refs_raw if clean_run(r))
    speaker = find_speaker(seg)
    title = _derive(seg, refs_raw, speaker)
    return {"title": title, "speaker": speaker, "ref": ref}


def parse_video(video: dict) -> dict | None:
    """Common case first (description line 1), fallback to the JSON title field.

    Returns {title, speaker, ref} or None when no scripture reference is found.
    """
    result = parse_line(first_line(video.get("description")))
    if not (result and result["ref"]):
        result = parse_line(norm(video.get("title")))
    if not (result and result["ref"]):
        return None

    # If the description-derived title is unusable (empty or still carries a
    # date/time header), re-derive upload_name from the JSON title field.
    if not result["title"] or re.search(
        r"\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{1,2}:\d{2}\s*(?:am|pm)?", result["title"]
    ):
        base = norm(video.get("title"))
        refs_t = find_refs(base)
        sp_t = find_speaker(base)
        fb = _derive(base, refs_t or [], sp_t)
        if fb:
            result["title"] = fb
    return result


# ---------------------------------------------------------------------------
# Migration emission (mirrors generate_media_migration.py)
# ---------------------------------------------------------------------------


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
    """Yield migration files, excluding the seed migration this script manages."""
    for f in sorted(versions_dir.glob("*.py")):
        if f.name.endswith("_seed_video_uploads_from_youtube.py"):
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
        down = re.search(r"^down_revision: [^=]*= (\"[^\"]+\"|None)", text, re.M)
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
    taken = existing_revisions(versions_dir)
    while True:
        rev = secrets.token_hex(6)
        if rev not in taken:
            return rev


def sql_str(value: str | None) -> str | None:
    """Escape a string for embedding inside a MySQL/MariaDB single-quoted literal."""
    if value is None:
        return None
    return value.replace("\\", "\\\\").replace("'", "''")


def build_row(
    video: dict, parsed: dict, owner_id: str
) -> tuple[str, str | None, str | None, str | None, str, str | None, str | None, str]:
    """Return (id, upload_location, upload_name, description, owner_id, speaker, ref, ts)."""
    video_id = video["id"]
    upload_date = video.get("upload_date") or ""
    if not re.fullmatch(r"\d{8}", upload_date):
        sys.exit(f"error: video {video_id} has invalid upload_date {upload_date!r}")
    ts = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]} 00:00:00"

    ref = parsed["ref"]
    if len(ref) > MAX_REFERENCE_LEN:
        sys.exit(
            f"error: video {video_id} reference_text exceeds {MAX_REFERENCE_LEN} chars "
            f"({len(ref)}): {ref!r}"
        )

    return (
        str(uuid.uuid5(MEDIA_NAMESPACE, f"youtube:{video_id}")),
        sql_str(video["url"]),
        sql_str(parsed["title"]),
        # Verbatim description (newlines preserved), matching the media seed.
        sql_str((video.get("description") or "").strip() or None),
        owner_id,
        sql_str(parsed["speaker"]),
        sql_str(ref),
        ts,
    )


def render_rows(rows: list[tuple]) -> str:
    """Render the VIDEO_UPLOAD_ROWS list body as Python source (repr() per value)."""
    lines = []
    for media_id, loc, name, desc, owner_id, speaker, ref, ts in rows:
        lines.append(
            f"    ({media_id!r}, {loc!r}, {name!r}, {desc!r}, {owner_id!r}, "
            f"{speaker!r}, {ref!r}, {ts!r}),  # youtube:{media_id[-12:]}"
        )
    return "\n".join(lines)


# The function bodies below contain real Python f-strings with braces, so they are
# kept verbatim and assembled by plain concatenation (never passed through .format()).
HEADER = '''"""seed video_uploads table from AFC Sacramento YouTube channel

Revision ID: {revision}
Revises: {down_revision_display}
Create Date: {create_date}

Data migration: one row per YouTube video that carries a scripture reference
(extracted via scripts/extract_youtube_services.py, parsed from the description's
first line ``[title - speaker • reference_text]``). Rows are idempotent — ids are
UUID5 of the YouTube video id (same value as the matching media row) and inserts
use ON DUPLICATE KEY UPDATE, so re-running after a fresh extraction only updates
changed values.
"""

from typing import Sequence, Union


from alembic import op

revision: str = "{revision}"
down_revision: Union[str, Sequence[str], None] = {down_revision_repr}
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (id, upload_location, upload_name, description, owner_id, speaker_name, reference_text,
#  media_association_date) — one tuple per YouTube video that carries a scripture reference.
VIDEO_UPLOAD_ROWS = [
'''

FOOTER = """
]


def _insert_sql(row: tuple) -> str:
    vid, loc, name, desc, owner_id, speaker, ref, ts = row
    desc_literal = "NULL" if desc is None else f"'{desc}'"
    speaker_literal = "NULL" if speaker is None else f"'{speaker}'"
    ref_literal = "NULL" if ref is None else f"'{ref}'"
    return (
        "INSERT INTO video_uploads "
        "(id, upload_location, upload_name, description, owner_id, speaker_name, "
        f"reference_text, media_association_date, created_on, updated_on) "
        f"VALUES ('{vid}', '{loc}', '{name}', {desc_literal}, '{owner_id}', "
        f"{speaker_literal}, {ref_literal}, '{ts}', '{ts}', '{ts}') "
        "ON DUPLICATE KEY UPDATE upload_location = VALUES(upload_location), "
        "upload_name = VALUES(upload_name), description = VALUES(description), "
        "speaker_name = VALUES(speaker_name), reference_text = VALUES(reference_text), "
        "media_association_date = VALUES(media_association_date), updated_on = VALUES(updated_on)"
    )


def upgrade() -> None:
    for row in VIDEO_UPLOAD_ROWS:
        op.execute(_insert_sql(row))


def downgrade() -> None:
    ids = ", ".join(f"'{row[0]}'" for row in VIDEO_UPLOAD_ROWS)
    op.execute(f"DELETE FROM video_uploads WHERE id IN ({ids})")
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
    """Locate a previously generated seed migration so regeneration replaces it in place."""
    for f in sorted(versions_dir.glob("*_seed_video_uploads_from_youtube.py")):
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

    rows = []
    skipped = 0
    for v in videos:
        parsed = parse_video(v)
        if not parsed:
            skipped += 1
            continue
        rows.append(build_row(v, parsed, args.owner_id))

    print(
        f"parsed {len(rows)} video_uploads rows from {len(videos)} videos "
        f"({skipped} skipped — no scripture reference)"
    )

    existing = None if args.out or args.dry_run else find_existing_seed_migration(VERSIONS_DIR)
    if existing:
        out_path, revision = existing
        print(f"regenerating existing migration in place: {out_path.name}")
    else:
        revision = new_revision_id(VERSIONS_DIR)
        out_path = args.out or VERSIONS_DIR / f"{revision}_seed_video_uploads_from_youtube.py"

    content = build_content(revision, head, render_rows(rows))

    if args.dry_run:
        print(content)
        return

    out_path.write_text(content)
    print(f"wrote {len(rows)} video_uploads rows to {out_path}")
    print(f"  down_revision: {head}")
    print("apply with: alembic upgrade head")


if __name__ == "__main__":
    main()

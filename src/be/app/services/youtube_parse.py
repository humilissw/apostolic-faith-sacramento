"""Parsing helpers for AFC Sacramento YouTube video metadata.

This is a faithful port of the parsing logic in
``scripts/generate_video_uploads_migration.py`` (kept self-contained there so
the script runs anywhere). In-app sync (see ``youtube_sync_service``) uses
this module so runtime-synced rows carry exactly the same parsed values as the
generated seed/append migrations.

If you change rules here, mirror them in the script (and vice versa).
"""

from __future__ import annotations

import re
import unicodedata

MAX_REFERENCE_LEN = 50  # video_uploads.reference_text max_length

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
# its numeric prefix was consumed by the previous book's chapter.
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
# book name + tail with no separator.
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
    """Clean one matched reference run into the reference_text value."""
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
    """Drop trailing book-name words the speaker regex over-captured."""
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
    """Strip a leading service header (date/time/weekday + service words)."""
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

    ``video`` here is a dict with "title" and "description" keys (the raw YouTube
    values). Returns {title, speaker, ref} or None when no scripture reference is
    found — mirrors the seed-migration rule that videos without a reference are
    not inserted into video_uploads.
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

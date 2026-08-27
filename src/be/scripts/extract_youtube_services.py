#!/usr/bin/env python3
"""Extract raw YouTube video metadata for the AFC Sacramento channel.

ELT step 1 (EXTRACT). This script only pulls data from YouTube and writes it
to a JSON file with the values exactly as YouTube reports them — no
transformation, no reformatting. Mapping that data into the ``media`` table
shape is a separate step (see transform_youtube_services.py).

Usage:
    # Live fetch from the channel (requires yt-dlp):
    python3 scripts/extract_youtube_services.py
    # or an explicit channel URL (default: https://www.youtube.com/@ApostolicFaithSacramento/videos)
    python3 scripts/extract_youtube_services.py --channel <channel /videos URL>

    # Or process a previously saved `yt-dlp -J` dump (no network needed):
    python3 scripts/extract_youtube_services.py --from-json /path/to/dump.json

    # Choose the output file:
    python3 scripts/extract_youtube_services.py --out data/youtube_services_raw.json

Live fetch requires yt-dlp. The script looks for ``yt-dlp`` on PATH first, then
falls back to ``uvx yt-dlp`` (ad-hoc, no install).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CHANNEL_URL = "https://www.youtube.com/@ApostolicFaithSacramento/videos"
REPO_BE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_BE_DIR / "data" / "youtube_services_raw.json"

# Raw fields captured per video, verbatim from yt-dlp's -J output.
RAW_FIELDS = (
    "id",
    "title",
    "description",
    "upload_date",  # YYYYMMDD as reported by YouTube
    "timestamp",  # unix epoch seconds as reported by YouTube
    "duration",
    "view_count",
)


def find_yt_dlp() -> list[str]:
    """Return the argv prefix that runs yt-dlp, or exit if none is found."""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    if shutil.which("uvx"):
        return ["uvx", "yt-dlp"]
    sys.exit(
        "error: yt-dlp not found on PATH and `uvx` is unavailable. "
        "Install it with `brew install yt-dlp` or `pipx install yt-dlp`."
    )


def fetch_channel_json(channel_url: str) -> dict:
    """Run yt-dlp and return the parsed full-playlist JSON for the channel."""
    cmd = [
        *find_yt_dlp(),
        "-J",  # dump full metadata as a single JSON document
        "--no-warnings",
        channel_url,
    ]
    print(f"running: {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"error: yt-dlp failed (exit {result.returncode}):\n{result.stderr[-2000:]}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"error: could not parse yt-dlp output as JSON: {exc}")


def extract_videos(channel_json: dict) -> list[dict]:
    """Pick out the raw fields we care about, untransformed."""
    videos = []
    for entry in channel_json.get("entries", []):
        video = {field: entry.get(field) for field in RAW_FIELDS}
        # Keep the canonical watch URL even when yt-dlp leaves it implicit.
        if not video.get("url"):
            video["url"] = f"https://www.youtube.com/watch?v={video['id']}"
        videos.append(video)

    # Deterministic ordering: newest first (by epoch timestamp, then id).
    videos.sort(key=lambda v: (-(v.get("timestamp") or 0), v["id"]))
    return videos


def load_dump(path: Path) -> dict:
    """Load a previously saved ``yt-dlp -J`` JSON dump."""
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: could not read yt-dlp dump {path}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--channel", default=DEFAULT_CHANNEL_URL, help="YouTube channel /videos URL (live fetch)"
    )
    source.add_argument(
        "--from-json",
        type=Path,
        dest="from_json",
        help="process a saved `yt-dlp -J` dump instead of fetching",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output JSON path")
    args = parser.parse_args()

    if args.from_json:
        channel_json = load_dump(args.from_json)
        source_label = str(args.from_json)
    else:
        channel_json = fetch_channel_json(args.channel)
        source_label = args.channel

    videos = extract_videos(channel_json)

    payload = {
        "source": {
            "channel": channel_json.get("channel"),
            "channel_id": channel_json.get("channel_id"),
            "url": source_label,
            "extracted_on": datetime.now(timezone.utc).isoformat(),
        },
        "video_count": len(videos),
        # Raw YouTube values, untransformed (ELT: extract first).
        "videos": videos,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(videos)} videos to {args.out}")


if __name__ == "__main__":
    main()

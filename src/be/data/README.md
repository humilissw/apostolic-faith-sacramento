# YouTube Services Data (ELT)

Raw extraction of all videos from the [AFC Sacramento YouTube channel](https://www.youtube.com/@ApostolicFaithSacramento),
plus the pipeline that turns them into `media` and `video_uploads` table rows.

## Files

- `youtube_services_raw.json` — raw extracted data: 310 videos (Aug 2022 → Aug 2026),
  each with YouTube's verbatim `title`, `description`, `upload_date` (YYYYMMDD),
  `timestamp`, `duration`, `view_count`, and watch URL. Newest first.

## Pipeline

```
EXTRACT   scripts/extract_youtube_services.py    YouTube -> youtube_services_raw.json
TRANSFORM scripts/generate_media_migration.py    raw JSON -> Alembic data migration (media table)
TRANSFORM scripts/generate_video_uploads_migration.py  raw JSON -> Alembic data migration (video_uploads table)
VALIDATE  scripts/_validate_media_migration.py   apply generated media migration to a scratch DB and assert
VALIDATE  scripts/_validate_video_uploads_migration.py  apply generated video_uploads migration to a scratch DB and assert
```

### 1. Extract

```bash
cd src/be
python3 scripts/extract_youtube_services.py            # live fetch (needs yt-dlp or uvx)
python3 scripts/extract_youtube_services.py --from-json /path/to/dump.json   # offline, from a saved `yt-dlp -J` dump
```

### 2. Generate the migration

```bash
python3 scripts/generate_media_migration.py            # writes app/alembic/versions/<rev>_seed_media_from_youtube.py
python3 scripts/generate_media_migration.py --dry-run  # print to stdout instead
```

Mapping (one `media` row per video):

| media column    | source                                   |
|-----------------|------------------------------------------|
| `id`            | UUID5(NAMESPACE_URL, "youtube:<video_id>") — deterministic across re-extractions |
| `name`          | YouTube title                            |
| `description`   | YouTube description (verbatim; NULL if empty) |
| `owner_id`      | `--owner-id` (default all-zeros UUID, same as the column's server_default) |
| `uploaded_on`   | YouTube upload date at midnight UTC      |
| `created_on`    | same as uploaded_on                      |
| `updated_on`    | same as uploaded_on                      |

The generated revision auto-chains onto the current alembic head. Inserts are
idempotent (`ON DUPLICATE KEY UPDATE name, description, updated_on`), so
regenerating after a new extraction and re-running only updates changed
titles/descriptions. The `description` column itself was added by migration
`p1q2r3s4t5u6_add_media_description.py`, which the seed revision chains on top of.

### 2b. Generate the video_uploads migration

```bash
python3 scripts/generate_video_uploads_migration.py            # writes app/alembic/versions/<rev>_seed_video_uploads_from_youtube.py
python3 scripts/generate_video_uploads_migration.py --dry-run  # print to stdout instead
```

Same raw JSON, second transform. One `video_uploads` row per video **that carries a
scripture reference** (videos with no reference are skipped). The generator parses
the description's first line, which follows `[title - speaker • reference_text]`:
the dash separates the sermon title from the speaker, the bullet ("•") separates the
speaker from the scripture reference. Each field is located by shape rather than
strict position (the order varies across the channel's history):

| video_uploads column        | source / rule                                                            |
|-----------------------------|--------------------------------------------------------------------------|
| `id`                        | UUID5(NAMESPACE_URL, "youtube:<video_id>") — same value as the matching `media` row |
| `upload_location`           | YouTube watch URL (`url`)                                                |
| `upload_name`               | sermon title (parsed; falls back to the JSON `title` field)              |
| `speaker_name`              | speaker — an honorific-prefixed name (Rev./Bro./Sis./etc.); NULL if absent. A segment containing ":" is scripture, never a speaker |
| `reference_text`            | scripture reference (≤50 chars); multiple references joined with "; ". The word "Scripture" introduces the reference that follows it and is discarded |
| `description`               | verbatim YouTube description (all lines, newlines preserved)             |
| `owner_id`                  | `--owner-id` (default all-zeros UUID, same server_default as media)      |
| `media_association_date`    | YouTube upload date (`upload_date`) at midnight UTC                      |
| `created_on` / `updated_on` | same as `media_association_date`                                         |

The reference regex tolerates the malformed variants present in the data (missing
colons like "Romans 12-2", double colons like "Isaiah 40:27:31", adjacent books like
"Revelation 2 Thessalonians 2:1-12") and never false-matches on date/time headers.
The generated revision chains onto the current alembic head (i.e. on top of the media
seed) and is idempotent (`ON DUPLICATE KEY UPDATE` over every derived column).

### 3. Apply / validate

```bash
alembic upgrade head                                   # apply (needs DB reachable; see src/be/.env)
python3 scripts/_validate_media_migration.py app/alembic/versions/<rev>_seed_media_from_youtube.py
python3 scripts/_validate_video_uploads_migration.py app/alembic/versions/<rev>_seed_video_uploads_from_youtube.py
```

Each validator drops/recreates only its table in the target DB, runs the generated
`upgrade()` twice and `downgrade()`, and asserts row count, apostrophe escaping
round-trip, column-length limits, midnight timestamps, and idempotency. (The
video_uploads validator also verifies verbatim description round-trip.)

### 4. Regenerate after a new extraction

```bash
python3 scripts/extract_youtube_services.py            # fresh raw JSON
python3 scripts/generate_media_migration.py
python3 scripts/generate_video_uploads_migration.py
alembic upgrade head
```

The generators **auto-chain onto the current alembic head**. If any migration was
added on top of the seeds since they were generated, regenerate will re-point the
seeds' `down_revision` at that head and create a cycle — Alembic rejects it. Safe
procedure when that has happened:

```bash
alembic downgrade <revision just before the media seed>   # e.g. p1q2r3s4t5u6
rm app/alembic/versions/*_seed_media_from_youtube.py \
   app/alembic/versions/*_seed_video_uploads_from_youtube.py \
   <any hand-written migrations built on top of the seeds>
python3 scripts/generate_media_migration.py
python3 scripts/generate_video_uploads_migration.py      # chains onto the new media seed
alembic upgrade head
```

Downgrading first matters: it removes the old revision ids from `alembic_version`
and deletes the seeded rows, so the regenerated revisions (new random ids) apply
cleanly. The seeds' `downgrade()` only deletes their own UUID5 rows, so any
non-seed rows in the tables survive — but back them up if you plan to run the
validators afterward (they DROP their table).

## Known data notes

- **Service date vs upload date**: for ~60% of videos the description states a
  service-occurrence date that differs from the YouTube upload date (e.g. service
  performed Sunday, uploaded a couple of days later). Per the task spec
  ("date the video was uploaded"), `uploaded_on` uses the **upload date**. The
  full verbatim description is preserved in `youtube_services_raw.json`, so the
  service date can be parsed and mapped (e.g. to a new column) in a later
  transform step without re-extracting.
- Titles are ≤100 chars (fits `media.name` max_length=200); 25 contain apostrophes
  — the generator SQL-escapes them (`'` → `''`) and the validator asserts they
  round-trip.
- Descriptions are ≤428 chars (fits `media.description` max_length=4000). The
  generator fails fast if a future extraction exceeds the column limit rather
  than silently truncating.
- **video_uploads coverage**: of the 310 videos, 203 carry a parseable scripture
  reference and are seeded into `video_uploads`; the remaining ~107 (music sets,
  ordinances, memorials, special programs, "Night of Music", etc.) have no
  reference in their title/description and are skipped by design. Reference text
  is ≤35 chars in the current extraction (well under the 50-char column).

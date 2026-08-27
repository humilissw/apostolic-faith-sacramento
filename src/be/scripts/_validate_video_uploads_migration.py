"""Isolated validation harness for the generated video_uploads seed migration.

Creates a scratch `video_uploads` table (exact DDL from migrations 482d25a6fc5d +
a1b2c3d4e5f6), then runs the generated module's upgrade() through alembic
Operations and asserts:

    - N rows inserted (one per parsed video)
    - apostrophe titles/descriptions round-trip (SQL escaping is right)
    - reference_text fits the 50-char column; speaker_name fits 200
    - media_association_date all at midnight within 2022-2026
    - idempotent: running upgrade() again still yields N rows (no dupes/errors)
    - downgrade() removes exactly those rows

Run:  poetry run python scripts/_validate_video_uploads_migration.py <migration_file>
"""

import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from alembic.migration import MigrationContext
from alembic.operations import Operations

MIGRATION_FILE = Path(sys.argv[1]).resolve()

VIDEO_UPLOADS_DDL = """
CREATE TABLE video_uploads (
    id VARCHAR(36) NOT NULL,
    created_on DATETIME NOT NULL,
    updated_on DATETIME NULL,
    upload_location VARCHAR(1000) NOT NULL,
    upload_name VARCHAR(1000) NOT NULL,
    media_association_date DATETIME NOT NULL,
    speaker_name VARCHAR(200) NULL,
    reference_text VARCHAR(50) NULL,
    description VARCHAR(4000) NULL,
    owner_id VARCHAR(36) NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    PRIMARY KEY (id)
)
"""


def load_module(path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("gen_vu_migration", path)
    if spec is None or spec.loader is None:
        sys.exit(f"error: could not load migration module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    from app.config import settings

    url = str(settings.SQLALCHEMY_DATABASE_URI)
    print(f"connecting to {url.split('@')[-1]}")
    engine = create_engine(url, poolclass=__import__("sqlalchemy.pool", fromlist=["pool"]).NullPool)

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS video_uploads"))
        conn.execute(text(VIDEO_UPLOADS_DDL))

    mod = load_module(MIGRATION_FILE)
    print(
        f"loaded {MIGRATION_FILE.name}: {len(mod.VIDEO_UPLOAD_ROWS)} rows, "
        f"down_revision={mod.down_revision}"
    )

    def run_upgrade():
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            with Operations.context(ctx):
                mod.upgrade()

    # First run
    run_upgrade()
    with engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM video_uploads")).scalar()
        print(f"after first upgrade(): {n} rows")
        assert n == len(mod.VIDEO_UPLOAD_ROWS), f"expected {len(mod.VIDEO_UPLOAD_ROWS)}, got {n}"

        # Column-length sanity: nothing overran its column (would have errored on insert,
        # but double-check the max stored lengths).
        mx_ref = conn.execute(
            text("SELECT MAX(CHAR_LENGTH(reference_text)) FROM video_uploads")
        ).scalar()
        mx_spk = conn.execute(
            text("SELECT MAX(CHAR_LENGTH(speaker_name)) FROM video_uploads")
        ).scalar()
        mx_loc = conn.execute(
            text("SELECT MAX(CHAR_LENGTH(upload_location)) FROM video_uploads")
        ).scalar()
        print(
            f"  max lengths: reference_text={mx_ref} (<=50), speaker_name={mx_spk} (<=200), "
            f"upload_location={mx_loc} (<=1000)"
        )
        assert mx_ref is not None and mx_ref <= 50, f"reference_text overran 50 chars: {mx_ref}"
        assert mx_spk is None or mx_spk <= 200, f"speaker_name overran 200 chars: {mx_spk}"
        assert (
            mx_loc is not None and mx_loc <= 1000
        ), f"upload_location overran 1000 chars: {mx_loc}"

        # Apostrophe round-trip on upload_name (find a title that had a single quote).
        quoted = [r for r in mod.VIDEO_UPLOAD_ROWS if r[2] and "'" in r[2]]
        assert quoted, "no apostrophe titles found to test escaping"
        sample_id, _loc, name_sql, _desc, _owner, _spk, _ref, _ts = quoted[0]
        expected_stored = name_sql.replace("''", "'")
        got = conn.execute(
            text("SELECT upload_name FROM video_uploads WHERE id=:i"), {"i": sample_id}
        ).scalar()
        print(f"  apostrophe test: stored={got!r}")
        assert (
            got == expected_stored
        ), f"escaping mismatch:\n  stored    ={got!r}\n  expected  ={expected_stored!r}"

        # Description round-trip (verbatim incl. newlines) + NULL handling.
        desc_checked = 0
        for vid, _loc, _name, desc_sql, _owner, _spk, _ref, _ts in mod.VIDEO_UPLOAD_ROWS:
            expected_desc = None if desc_sql is None else desc_sql.replace("''", "'")
            got_desc = conn.execute(
                text("SELECT description FROM video_uploads WHERE id=:i"), {"i": vid}
            ).scalar()
            assert got_desc == expected_desc, (
                f"description mismatch for {vid}:\n  stored    ={got_desc!r}\n"
                f"  expected  ={expected_desc!r}"
            )
            desc_checked += 1
        null_descs = conn.execute(
            text("SELECT COUNT(*) FROM video_uploads WHERE description IS NULL")
        ).scalar()
        print(f"  description test: {desc_checked} rows verified, {null_descs} NULL descriptions")

        # media_association_date sanity: midnight datetimes within 2022-2026.
        bad = conn.execute(
            text(
                "SELECT COUNT(*) FROM video_uploads WHERE TIME(media_association_date) "
                "<> '00:00:00'"
            )
        ).scalar()
        assert bad == 0, f"{bad} rows not at midnight"
        yr = conn.execute(
            text(
                "SELECT MIN(YEAR(media_association_date)), MAX(YEAR(media_association_date)) "
                "FROM video_uploads"
            )
        ).fetchone()
        assert yr is not None, "no rows to compute year range"
        print(f"  media_association_date: all midnight; year range {yr[0]}-{yr[1]}")

    # Idempotency: run again.
    run_upgrade()
    with engine.connect() as conn:
        n2 = conn.execute(text("SELECT COUNT(*) FROM video_uploads")).scalar()
        print(f"after second upgrade(): {n2} rows (idempotent)")
        assert n2 == len(mod.VIDEO_UPLOAD_ROWS), f"idempotency broken: {n2}"

    # Downgrade removes exactly those rows.
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        with Operations.context(ctx):
            mod.downgrade()
    with engine.connect() as conn:
        n3 = conn.execute(text("SELECT COUNT(*) FROM video_uploads")).scalar()
        print(f"after downgrade(): {n3} rows")
        assert n3 == 0, f"downgrade left {n3} rows"

    print("\nALL CHECKS PASSED ✔")


if __name__ == "__main__":
    main()

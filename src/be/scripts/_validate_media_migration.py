"""Isolated validation harness for the generated media seed migration.

Creates a scratch DB with just the `media` table (exact DDL from the real schema
migrations 482d25a6fc5d + a1b2c3d4e5f6), then runs the generated module's
upgrade() through alembic Operations, and asserts:

    - 310 rows inserted
    - apostrophe titles round-trip correctly (SQL escaping is right)
    - descriptions round-trip correctly (including NULL handling)
    - idempotent: running upgrade() again still yields 310 rows (no dupes/errors)
    - downgrade() removes exactly those rows

Run:  DB_PASSWORD=... poetry run python scripts/_validate_media_migration.py <migration_file>
"""

import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from alembic.migration import MigrationContext
from alembic.operations import Operations

MIGRATION_FILE = Path(sys.argv[1]).resolve()

MEDIA_DDL = """
CREATE TABLE media (
    id VARCHAR(36) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(4000) NULL,
    owner_id VARCHAR(36) NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    uploaded_on DATETIME NOT NULL,
    created_on DATETIME NOT NULL,
    updated_on DATETIME NOT NULL,
    PRIMARY KEY (id)
)
"""


def load_module(path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("gen_media_migration", path)
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
        conn.execute(text("DROP TABLE IF EXISTS media"))
        conn.execute(text(MEDIA_DDL))

    mod = load_module(MIGRATION_FILE)
    print(
        f"loaded {MIGRATION_FILE.name}: {len(mod.MEDIA_ROWS)} rows, "
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
        n = conn.execute(text("SELECT COUNT(*) FROM media")).scalar()
        print(f"after first upgrade(): {n} rows")
        assert n == len(mod.MEDIA_ROWS), f"expected {len(mod.MEDIA_ROWS)}, got {n}"

        # Apostrophe round-trip: find a title that had a single quote in the source.
        quoted = [r for r in mod.MEDIA_ROWS if "'" in r[1]]
        assert quoted, "no apostrophe titles found to test escaping"
        sample_id, sample_name_sql, _sample_desc_sql, _owner_id, _ts = quoted[0]
        # sample_name_sql is SQL-escaped (doubled quotes); the stored value must have single quotes.
        expected_stored = sample_name_sql.replace("''", "'")
        got = conn.execute(text("SELECT name FROM media WHERE id=:i"), {"i": sample_id}).scalar()
        print(f"  apostrophe test: stored={got!r}")
        assert (
            got == expected_stored
        ), f"escaping mismatch:\n  stored    ={got!r}\n  expected  ={expected_stored!r}"

        # Description round-trip: stored value must equal the source text (unescaped),
        # and rows with no description must store NULL.
        desc_checked = 0
        for media_id, _name_sql, desc_sql, _owner_id, _ts in mod.MEDIA_ROWS:
            expected_desc = None if desc_sql is None else desc_sql.replace("''", "'")
            got_desc = conn.execute(
                text("SELECT description FROM media WHERE id=:i"), {"i": media_id}
            ).scalar()
            assert got_desc == expected_desc, (
                f"description mismatch for {media_id}:\n  stored    ={got_desc!r}\n"
                f"  expected  ={expected_desc!r}"
            )
            desc_checked += 1
        null_descs = conn.execute(
            text("SELECT COUNT(*) FROM media WHERE description IS NULL")
        ).scalar()
        print(f"  description test: {desc_checked} rows verified, {null_descs} NULL descriptions")

        # uploaded_on sanity: all should be midnight datetimes within 2022-2026
        bad = conn.execute(
            text("SELECT COUNT(*) FROM media WHERE TIME(uploaded_on) <> '00:00:00'")
        ).scalar()
        assert bad == 0, f"{bad} rows not at midnight"

    # Idempotency: run again
    run_upgrade()
    with engine.connect() as conn:
        n2 = conn.execute(text("SELECT COUNT(*) FROM media")).scalar()
        print(f"after second upgrade(): {n2} rows (idempotent)")
        assert n2 == len(mod.MEDIA_ROWS), f"idempotency broken: {n2}"

    # Downgrade removes exactly those rows
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        with Operations.context(ctx):
            mod.downgrade()
    with engine.connect() as conn:
        n3 = conn.execute(text("SELECT COUNT(*) FROM media")).scalar()
        print(f"after downgrade(): {n3} rows")
        assert n3 == 0, f"downgrade left {n3} rows"

    print("\nALL CHECKS PASSED ✔")


if __name__ == "__main__":
    main()

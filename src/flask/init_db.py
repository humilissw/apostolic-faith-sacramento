#!/usr/bin/env python3
"""Initialize the database: create DB (if needed) + run alembic migrations.

Usage:
    python init_db.py

Reads DB config from .env file in the same directory as this script.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def get_config():
    """Load .env and return DB config dict."""
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path, override=True)

    return {
        "host": os.environ.get("DB_SERVER", "127.0.0.1"),
        "port": int(os.environ.get("DB_PORT", 3306)),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_DB", ""),
    }


def create_database(config):
    """Create the database if it doesn't exist."""
    uri = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/"
    engine = create_engine(uri)
    db_name = config["database"]

    with engine.connect() as conn:
        result = conn.execute(text("SHOW DATABASES"))
        dbs = [row[0] for row in result]

    if db_name not in dbs:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE `{db_name}`"))
            conn.commit()
        print(f"Created database: {db_name}")
    else:
        print(f"Database already exists: {db_name}")
    engine.dispose()


def run_migrations(config):
    """Run alembic migrations."""
    alembic_dir = Path(__file__).parent / "backend" / "alembic"
    if not alembic_dir.exists():
        print(f"Alembic directory not found at {alembic_dir}")
        sys.exit(1)

    # Create alembic.ini if it doesn't exist
    ini_path = alembic_dir / "alembic.ini"
    if not ini_path.exists():
        ini_path.write_text(
            f"""
[alembic]
script_location = {alembic_dir.resolve()}/alembic
sqlalchemy.url = mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        )

    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config(str(ini_path))
    command.upgrade(alembic_cfg, "head")
    print("Migrations complete.")


if __name__ == "__main__":
    config = get_config()
    print(f"Config: {config['host']}:{config['port']}/{config['database']} (user: {config['user']})")
    print()

    create_database(config)
    print()
    run_migrations(config)
    print("\nDatabase initialized successfully.")

"""Shared test fixtures with MariaDB (real test DB)."""

import uuid
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import pymysql
import sqlalchemy
from sqlalchemy.orm import sessionmaker


# Disable SSL for all pymysql connections in tests (Docker MariaDB doesn't support SSL)
_orig_connect = pymysql.connect


def _patched_connect(**kwargs):
    kwargs["ssl_disabled"] = True
    return _orig_connect(**kwargs)


pymysql.connect = _patched_connect


# ─── RSA keys ───

_TEST_DIR = Path(__file__).parent
_RSA_PRIVATE = _TEST_DIR / "test_private.pem"
_RSA_PUBLIC = _TEST_DIR / "test_public.pem"


def _generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    _RSA_PRIVATE.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    _RSA_PUBLIC.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return str(_RSA_PRIVATE), str(_RSA_PUBLIC)


_TEST_RSA_PRIV, _TEST_RSA_PUB = _generate_rsa_keys()


# Import backend (after pymysql patch)
from backend.core import db as db_module
from backend.models import *  # noqa: F401, F403
from backend.config import settings as _test_settings

# Patch engine to use flask_test DB
# Must NOT use str(db_module.engine.url) — SQLAlchemy masks password as *** in URL repr
_new_url = f"mysql+pymysql://{_test_settings.DB_USER}:{_test_settings.DB_PASSWORD}" f"@{_test_settings.DB_SERVER}:{_test_settings.DB_PORT}/flask_test"
db_module.engine = sqlalchemy.create_engine(_new_url, pool_pre_ping=True)
db_module.SyncSessionLocal = sessionmaker(bind=db_module.engine, expire_on_commit=False)

# Also patch in deps (caches SyncSessionLocal at import time)
import backend.api.deps as deps_module

deps_module.SyncSessionLocal = db_module.SyncSessionLocal


@pytest.fixture(scope="session")
def rsa_keys():
    return (str(_RSA_PRIVATE), str(_RSA_PUBLIC))


def _seed_superuser():
    """Create the default superuser if not exists."""
    from backend.config import settings
    from backend.models import User, UserScope
    from backend.core.security import get_password_hash
    from sqlmodel import Session, select

    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    _TEST_USER_EMAIL = settings.FIRST_SUPERUSER
    _TEST_USER_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD

    with Session(db_module.engine) as session:
        stmt = select(User).where(User.email == _TEST_USER_EMAIL)
        existing = session.exec(stmt).first()
        if existing:
            return

        uid = str(uuid.uuid4())
        sid = str(uuid.uuid4())
        session.add(
            User(
                id=uid,
                email=_TEST_USER_EMAIL,
                hashed_password=get_password_hash(_TEST_USER_PASSWORD),
                is_active=True,
                is_superuser=True,
                created_on=now,
                new_id=str(uuid.uuid4()),
            )
        )
        session.add(UserScope(id=sid, user_id=uid, scope="superuser", created_on=now))
        session.commit()


# Export test credentials for test modules
_TEST_USER_EMAIL = _test_settings.FIRST_SUPERUSER
_TEST_USER_PASSWORD = _test_settings.FIRST_SUPERUSER_PASSWORD


@pytest.fixture(scope="session")
def app():
    """Test app with MariaDB (flask_test)."""
    from backend import create_app
    from sqlmodel import SQLModel
    from backend.models import User
    from backend.core.security import get_password_hash
    from sqlalchemy import select
    from sqlmodel import Session

    SQLModel.metadata.drop_all(db_module.engine)
    SQLModel.metadata.create_all(db_module.engine)
    _seed_superuser()

    app = create_app()
    app.config["TESTING"] = True
    yield app
    # Reset admin password to original in case test_update_pw changed it
    with Session(db_module.engine) as s:
        admin = s.exec(select(User).where(User.email == _TEST_USER_EMAIL)).first()
        if admin:
            from backend.core.security import get_password_hash

            s.execute(
                __import__("sqlalchemy")
                .update(User)
                .where(User.email == _TEST_USER_EMAIL)
                .values(hashed_password=get_password_hash(_TEST_USER_PASSWORD))
            )
            s.commit()
    SQLModel.metadata.drop_all(db_module.engine)


@pytest.fixture
def client(app):
    return app.test_client()


def _auth_headers(client):
    """Get auth headers for a request."""
    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": _TEST_USER_EMAIL, "password": _TEST_USER_PASSWORD},
        content_type="multipart/form-data",
    )
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

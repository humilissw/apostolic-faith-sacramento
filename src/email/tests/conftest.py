"""Shared fixtures for the email service tests.

Uses the real backend keypair (src/be/security_keys) so the RS256 verification
path is exercised exactly as in production: tokens signed with the private key
verify against the public key this service loads.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
BE_KEYS = SERVICE_ROOT.parent / "be" / "security_keys"

os.environ.update(
    {
        "RSA_PUB_KEY": str(BE_KEYS / "public_key.pem"),
        "SMTP_HOST": "localhost",
        "SMTP_PORT": "1025",
        "SMTP_TLS": "False",
        "SMTP_SSL": "False",
        "EMAILS_FROM_EMAIL": "test@afc.org",
        "EMAILS_FROM_NAME": "AFC Test",
        "FRONTEND_HOST": "https://fe.test",
        "SERVICE_API_KEY": "test-service-key",
        "TRACKING_DB_URL": "sqlite:///:memory:",
        "DB_SERVER": "",  # shared users DB unavailable in unit tests
    }
)
sys.path.insert(0, str(SERVICE_ROOT))

import jwt
import pytest
from fastapi.testclient import TestClient

PRIVATE_KEY = (BE_KEYS / "private_dec.pem").read_text()


def make_token(scopes: list[str], sub: str = "tester@afc.org") -> str:
    return jwt.encode({"sub": sub, "scopes": scopes}, PRIVATE_KEY, algorithm="RS256")


@pytest.fixture()
def client(monkeypatch) -> TestClient:
    # Isolate the tracking DB per test (in-memory, fresh schema each time).
    from app.core import tracking

    tracking.tracking_session_factory.cache_clear()
    from app.main import app

    return TestClient(app)


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(['api:email'])}"}


@pytest.fixture()
def no_scope_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(['users:read'])}"}


@pytest.fixture()
def api_key_headers() -> dict[str, str]:
    return {"X-API-Key": "test-service-key"}

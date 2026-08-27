"""Pytest fixtures for the BFF test suite.

A fake upstream FastAPI backend is simulated with ``httpx.MockTransport`` so no
network access is needed. The mock records every request it receives (method,
path, headers, body) so tests can assert on what the BFF forwarded.
"""

from __future__ import annotations

import json

import httpx
import pytest

from app.app import create_app
from app.config import Settings


class MockBackend:
    """Records requests and returns canned responses keyed by (method, path)."""

    def __init__(self) -> None:
        self.requests: list[dict] = []
        self.routes: dict[tuple[str, str], httpx.Response] = {}
        # Routes that return a fresh response per call (used for 401-then-retry).
        self.routes_seq: dict[tuple[str, str], list[httpx.Response]] = {}

    def set_route(self, method: str, path: str, response: httpx.Response) -> None:
        self.routes[(method.upper(), path)] = response

    def set_route_sequence(self, method: str, path: str, responses: list[httpx.Response]) -> None:
        """Return each response in order on successive calls to (method, path)."""
        self.routes_seq[(method.upper(), path)] = list(responses)

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(
            {
                "method": request.method,
                "path": request.url.path,
                "target": str(request.url),  # full URL incl. query string
                "headers": dict(request.headers),
                "body": request.content,
            }
        )

        key = (request.method.upper(), request.url.path)
        if key in self.routes_seq:
            seq = self.routes_seq[key]
            return seq.pop(0) if len(seq) > 1 else seq[0]
        if key in self.routes:
            return self.routes[key]

        # Default: 404 with FastAPI-style body.
        return httpx.Response(404, json={"detail": "Not Found"})


def make_settings(
    backend_url: str = "https://backend.test",
    spa_origins: list[str] | None = None,
    spa_url: str = "https://spa.test",
    secret_key: str = "test-secret-key",  # nosec B107 -- dummy value for tests only
    session_cookie_secure: bool = False,  # allow cookie assertions in tests
    auth_code_ttl_seconds: int = 120,
) -> Settings:
    return Settings(
        BACKEND_URL=backend_url,
        BACKEND_VERIFY=True,
        SPA_ORIGINS=spa_origins if spa_origins is not None else ["https://spa.test"],
        SPA_URL=spa_url,
        SECRET_KEY=secret_key,
        SESSION_COOKIE_SECURE=session_cookie_secure,
        AUTH_CODE_TTL_SECONDS=auth_code_ttl_seconds,
    )


@pytest.fixture()
def mock_backend():
    return MockBackend()


@pytest.fixture()
def app(mock_backend):
    settings = make_settings()
    flask_app = create_app(settings)

    # Swap in a client that talks to the mock backend instead of the network.
    from app.proxy import build_backend_client  # noqa: F401 - kept for clarity

    transport = httpx.MockTransport(mock_backend.handler)
    client = httpx.Client(
        base_url=settings.BACKEND_URL,
        transport=transport,
        follow_redirects=False,
    )
    flask_app.config["BACKEND_CLIENT"] = client

    # Reset any in-memory auth-code state between tests.
    from app import security

    security.reset_auth_codes()

    yield flask_app
    client.close()


@pytest.fixture()
def client(app):
    with app.test_client() as test_client:
        yield test_client


# --- Convenience builders for canned backend responses --------------------- #


def token_response(access="ACCESS", refresh="REFRESH"):
    return httpx.Response(
        200,
        json={
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "access_token_expires": 600,
            "refresh_token_expires": 86400,
            "scopes": ["api:all"],
        },
    )


def refresh_response(access="NEW_ACCESS", refresh="NEW_REFRESH"):
    """Refresh response: JSON carries the new access token; Set-Cookie carries it too.

    The BFF reads the rotated access token from the ``Set-Cookie`` header when
    present and falls back to the JSON body otherwise (both are exercised by the
    test suite). The rotated refresh token travels only in Set-Cookie upstream,
    so the BFF keeps its stored value here.
    """
    return httpx.Response(
        200,
        json={
            "access_token": access,
            "token_type": "bearer",
            "access_token_expires": 600,
            "scopes": ["api:all"],
        },
        headers={"Set-Cookie": f"access_token={access}; Path=/; Secure; HttpOnly; SameSite=None"},
    )


def me_response(email="user@example.com"):
    return httpx.Response(
        200,
        json={
            "email": email,
            "is_active": True,
            "id": "u-1",
            "new_id": "n-1",
            "full_name": "Test User",
            "assigned_scopes": ["api:all"],
        },
    )


def json_body(obj) -> str:
    return json.dumps(obj)

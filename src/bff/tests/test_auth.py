"""Tests for server-side authentication (login, code exchange, me, refresh, logout)."""

from __future__ import annotations

import re

import httpx
from conftest import me_response, refresh_response, token_response


def _login(  # nosec B107 -- dummy test credentials, not a real secret
    client, mock_backend, username="user@example.com", password="hunter2"
):
    """Log in (form-encoded) and return the one-time code from the redirect."""
    mock_backend.set_route("POST", "/api/v1/login/access-token", token_response())
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 302
    location = resp.headers["Location"]
    code = re.search(r"code=([^&]+)", location).group(1)
    return code


def test_login_redirects_to_spa_with_code(client, mock_backend):
    _login(client, mock_backend)

    # The backend received a form-encoded password grant.
    assert len(mock_backend.requests) == 1
    req = mock_backend.requests[0]
    assert req["method"] == "POST"
    assert req["path"] == "/api/v1/login/access-token"
    body = req["body"].decode()
    assert "username=user%40example.com" in body
    assert "password=hunter2" in body
    assert "scope=api%3Aall" in body


def test_login_sets_session_cookie(client, mock_backend):
    _login(client, mock_backend)
    # The signed session cookie is stored in the client's jar after login.
    assert client.get_cookie("bff_session") is not None


def test_login_no_credentials_is_400(client, mock_backend):
    resp = client.post(
        "/auth/login",
        data={"username": "", "password": ""},
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 400
    # No backend call should have been made.
    assert mock_backend.requests == []


def test_login_backend_failure_passes_through(client, mock_backend):
    mock_backend.set_route(
        "POST",
        "/api/v1/login/access-token",
        httpx.Response(400, json={"detail": "Incorrect email or password"}),
    )
    resp = client.post(
        "/auth/login",
        data={"username": "u@e.com", "password": "bad"},
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 400
    assert resp.get_json()["detail"] == "Incorrect email or password"


def test_login_redirect_false_returns_json(client, mock_backend):
    mock_backend.set_route("POST", "/api/v1/login/access-token", token_response())
    resp = client.post(
        "/auth/login?redirect=false",
        data={"username": "u@e.com", "password": "pw"},
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["code"]
    assert data["redirect_url"].startswith("https://spa.test/?code=")


def test_session_exchange_success(client, mock_backend):
    code = _login(client, mock_backend)
    resp = client.post("/auth/session", json={"code": code})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["user"]["email"] == "user@example.com"


def test_session_exchange_invalid_code_is_401(client, mock_backend):
    _login(client, mock_backend)
    resp = client.post("/auth/session", json={"code": "not-a-real-code"})
    assert resp.status_code == 401


def test_session_exchange_reused_code_is_401(client, mock_backend):
    code = _login(client, mock_backend)
    first = client.post("/auth/session", json={"code": code})
    assert first.status_code == 200
    # Second use of the same one-time code must fail.
    second = client.post("/auth/session", json={"code": code})
    assert second.status_code == 401


def test_me_returns_user_and_injects_bearer(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route("GET", "/api/v1/auth/me", me_response())

    resp = client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "user@example.com"

    # The forwarded request carried the access token as a Bearer header.
    req = mock_backend.requests[-1]
    assert req["path"] == "/api/v1/auth/me"
    assert req["headers"].get("authorization") == "Bearer ACCESS"


def test_me_unauthenticated_is_401(client, mock_backend):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
    assert mock_backend.requests == []


def test_me_refreshes_expired_token_then_retries(client, mock_backend):
    _login(client, mock_backend)
    # First /auth/me is rejected (expired access token); refresh rotates to
    # NEW_ACCESS; the retry succeeds.
    mock_backend.set_route("POST", "/api/v1/login/refresh-token", refresh_response())
    mock_backend.set_route_sequence(
        "GET",
        "/api/v1/auth/me",
        [
            httpx.Response(401, json={"detail": "Not authenticated"}),
            me_response(),
        ],
    )

    resp = client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "user@example.com"

    # A refresh call was made, then a retry with the new token.
    paths = [r["path"] for r in mock_backend.requests]
    assert "/api/v1/login/refresh-token" in paths
    assert any(
        r["path"] == "/api/v1/auth/me" and r["headers"].get("authorization") == "Bearer NEW_ACCESS"
        for r in mock_backend.requests
    )


def test_logout_clears_session_and_revokes(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route(
        "POST", "/api/v1/login/logout", httpx.Response(200, json={"message": "Logged out"})
    )

    resp = client.post("/auth/logout")
    assert resp.status_code == 200

    # Backend logout was called with the bearer token.
    logout_req = next(r for r in mock_backend.requests if r["path"] == "/api/v1/login/logout")
    assert logout_req["headers"].get("authorization") == "Bearer ACCESS"

    # Session is cleared: /auth/me now 401s without hitting the backend again.
    before = len(mock_backend.requests)
    me_resp = client.get("/auth/me")
    assert me_resp.status_code == 401
    assert len(mock_backend.requests) == before


def test_refresh_endpoint(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route("POST", "/api/v1/login/refresh-token", refresh_response())

    resp = client.post("/auth/refresh")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True

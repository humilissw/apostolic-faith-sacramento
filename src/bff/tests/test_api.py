"""Tests for /api/v1/* forwarding: token injection, body/query passthrough, 401 retry."""

from __future__ import annotations

import httpx
from conftest import refresh_response, token_response


def _login(client, mock_backend):
    mock_backend.set_route("POST", "/api/v1/login/access-token", token_response())
    client.post(
        "/auth/login",
        data={"username": "u@e.com", "password": "pw"},
        content_type="application/x-www-form-urlencoded",
    )


def test_get_forwards_with_bearer(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route(
        "GET", "/api/v1/feature-flags/", httpx.Response(200, json={"data": [], "count": 0})
    )

    resp = client.get("/api/v1/feature-flags/")
    assert resp.status_code == 200
    assert resp.get_json() == {"data": [], "count": 0}

    req = mock_backend.requests[-1]
    assert req["method"] == "GET"
    assert req["path"] == "/api/v1/feature-flags/"
    assert req["headers"].get("authorization") == "Bearer ACCESS"


def test_query_string_is_forwarded(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route(
        "GET", "/api/v1/users/", httpx.Response(200, json={"data": [], "count": 0})
    )

    resp = client.get("/api/v1/users/?skip=0&limit=50")
    assert resp.status_code == 200

    req = mock_backend.requests[-1]
    # Both query params must survive the round-trip to the backend.
    assert "skip=0" in req["target"]
    assert "limit=50" in req["target"]


def test_post_json_body_is_forwarded(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route(
        "POST", "/api/v1/video-uploads/", httpx.Response(201, json={"id": "v-1"})
    )

    resp = client.post(
        "/api/v1/video-uploads/",
        json={"upload_name": "Sermon 1", "upload_location": "https://youtu.be/x"},
    )
    assert resp.status_code == 201
    assert resp.get_json() == {"id": "v-1"}

    req = mock_backend.requests[-1]
    assert req["method"] == "POST"
    body = req["body"].decode()
    assert '"upload_name"' in body and "Sermon 1" in body
    assert req["headers"].get("authorization") == "Bearer ACCESS"


def test_unauthenticated_api_passes_through_without_bearer(client, mock_backend):
    # No login: the BFF should still forward (no Authorization header) and let
    # the backend decide (e.g. 401).
    mock_backend.set_route(
        "GET", "/api/v1/scheduler/", httpx.Response(401, json={"detail": "Not authenticated"})
    )
    resp = client.get("/api/v1/scheduler/")
    assert resp.status_code == 401

    req = mock_backend.requests[-1]
    assert "authorization" not in req["headers"]


def test_401_triggers_refresh_and_retry(client, mock_backend):
    _login(client, mock_backend)
    # First scheduler call -> 401 (expired access token); retry with the new
    # token -> 200. Refresh rotates to NEW_ACCESS.
    mock_backend.set_route("POST", "/api/v1/login/refresh-token", refresh_response())
    mock_backend.set_route_sequence(
        "GET",
        "/api/v1/scheduler/",
        [
            httpx.Response(401, json={"detail": "Not authenticated"}),
            httpx.Response(200, json={"data": [], "count": 0}),
        ],
    )

    resp = client.get("/api/v1/scheduler/")
    assert resp.status_code == 200
    assert resp.get_json() == {"data": [], "count": 0}

    paths = [r["path"] for r in mock_backend.requests]
    assert "/api/v1/login/refresh-token" in paths
    # The retry carried the refreshed access token.
    retried = [r for r in mock_backend.requests if r["path"] == "/api/v1/scheduler/"]
    assert any(r["headers"].get("authorization") == "Bearer NEW_ACCESS" for r in retried)


def test_401_without_refresh_token_is_not_retried(client, mock_backend):
    # Log in but clear the refresh token from the session to simulate none.
    _login(client, mock_backend)
    with client.session_transaction() as sess:
        sess["refresh_token"] = ""  # nosec B105 -- intentional clear for test setup

    mock_backend.set_route(
        "GET", "/api/v1/scheduler/", httpx.Response(401, json={"detail": "Not authenticated"})
    )
    resp = client.get("/api/v1/scheduler/")
    assert resp.status_code == 401
    # No refresh call should have been attempted.
    assert all(r["path"] != "/api/v1/login/refresh-token" for r in mock_backend.requests)


def test_error_body_passes_through_verbatim(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route(
        "POST", "/api/v1/scheduler/", httpx.Response(409, json={"detail": {"message": "conflict"}})
    )
    resp = client.post("/api/v1/scheduler/", json={"user_id": "u", "event_date": "2026-01-01"})
    assert resp.status_code == 409
    assert resp.get_json()["detail"]["message"] == "conflict"


def test_5xx_passes_through(client, mock_backend):
    _login(client, mock_backend)
    mock_backend.set_route("GET", "/api/v1/users/", httpx.Response(500, text="boom"))
    resp = client.get("/api/v1/users/")
    assert resp.status_code == 500
    assert resp.get_data(as_text=True) == "boom"

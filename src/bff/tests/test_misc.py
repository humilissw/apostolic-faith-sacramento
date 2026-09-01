"""Tests for CORS, health, root metadata, and error handling."""

from __future__ import annotations

from conftest import token_response


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_root_metadata(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "afc-sacramento-bff"
    assert "/auth/login" in data["endpoints"]["login"]


def test_cors_allows_configured_origin(client, mock_backend):
    mock_backend.set_route("POST", "/api/v1/login/access-token", token_response())
    resp = client.post(
        "/auth/login",
        data={"username": "u@e.com", "password": "pw"},
        content_type="application/x-www-form-urlencoded",
        headers={"Origin": "https://spa.test"},
    )
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://spa.test"
    assert resp.headers.get("Access-Control-Allow-Credentials") == "true"


def test_cors_blocks_unknown_origin(client):
    resp = client.get("/health", headers={"Origin": "https://evil.example.com"})
    # No allow-origin header for an origin not in SPA_ORIGINS.
    assert "Access-Control-Allow-Origin" not in resp.headers


def test_no_origin_means_no_cors_headers(client):
    resp = client.get("/health")
    assert "Access-Control-Allow-Origin" not in resp.headers


def test_404_returns_json_detail(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert resp.get_json() == {"detail": "Not Found"}


def test_security_headers_present(client):
    resp = client.get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("Referrer-Policy") == "no-referrer"

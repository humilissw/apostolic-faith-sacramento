"""Tests for upstream TLS handling in app.proxy (no network)."""

from __future__ import annotations

import ssl

from app.config import Settings
from app.proxy import _build_ssl_context


def _settings(verify: bool, url: str) -> Settings:
    return Settings(BACKEND_URL=url, BACKEND_VERIFY=verify)


def test_verify_on_builds_verifying_context():
    ctx = _build_ssl_context(_settings(True, "https://backend:8000"))
    assert isinstance(ctx, ssl.SSLContext)
    # A verifying context checks the peer cert by default.
    assert ctx.verify_mode == ssl.CERT_REQUIRED


def test_verify_off_non_loopback_builds_unverified_context():
    # Regression: the compose service name `backend` is not loopback. Disabling
    # verification for it must succeed (self-signed dev stack), not raise.
    ctx = _build_ssl_context(_settings(False, "https://backend:8000"))
    assert isinstance(ctx, ssl.SSLContext)
    assert ctx.verify_mode == ssl.CERT_NONE
    assert ctx.check_hostname is False


def test_verify_off_loopback_builds_unverified_context():
    ctx = _build_ssl_context(_settings(False, "https://localhost:8000"))
    assert isinstance(ctx, ssl.SSLContext)
    assert ctx.verify_mode == ssl.CERT_NONE

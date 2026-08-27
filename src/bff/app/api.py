"""Forward ``/api/v1/*`` to the backend, injecting the access token.

This is a hand-rolled proxy (no tunnel library): every request under
``/api/v1/`` is forwarded verbatim (method, path, query, body, relevant headers)
with an ``Authorization: *** header added from the BFF session. If the backend
answers 401 and the session still holds a refresh token, the BFF refreshes once
and retries — mirroring the SPA's own 401-retry behaviour but server-side.
"""

from __future__ import annotations

import json
import logging

from flask import Response, current_app, request, session

from app.config import Settings
from app.proxy import forward, forward_request
from app.security import StoredSession, session_get, session_set

logger = logging.getLogger(__name__)


def _settings() -> Settings:  # type: ignore[no-untyped-def]
    return current_app.config["SETTINGS"]


def _backend_client():  # type: ignore[no-untyped-def]
    return current_app.config["BACKEND_CLIENT"]


def _refresh_once(client, settings: Settings) -> bool:  # type: ignore[no-untyped-def]
    """Attempt a one-time token refresh using the stored refresh token."""
    stored = session_get(session)
    if not stored.refresh_token:
        return False

    body = json.dumps({"refresh_token": stored.refresh_token}).encode()
    resp, cookies = forward(
        client,
        method="POST",
        path="/api/v1/login/refresh-token",
        body=body,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        logger.warning("BFF token refresh failed with status %s", resp.status_code)
        return False

    updated = StoredSession(
        access_token=cookies.get("access_token") or "",
        refresh_token=cookies.get("refresh_token") or stored.refresh_token,
        user=stored.user,
    )
    if not updated.access_token:
        try:
            updated.access_token = resp.get_json().get("access_token", "")
        except ValueError:
            pass
    if not updated.access_token:
        return False

    session_set(session, updated)
    return True


def _apply_auth_cookies(cookies: dict[str, str]) -> None:  # type: ignore[no-untyped-def]
    """Keep the BFF session in sync with any rotated tokens from the backend."""
    if not cookies:
        return
    stored = session_get(session)
    if cookies.get("access_token"):
        stored.access_token = cookies["access_token"]
    if "refresh_token" in cookies and cookies["refresh_token"]:
        stored.refresh_token = cookies["refresh_token"]
    elif "refresh_token" in cookies:  # empty value -> backend cleared it
        stored.refresh_token = ""  # nosec B105 -- intentional clear, not a password
    session_set(session, stored)


def handle_api() -> Response:  # type: ignore[return]
    """Single handler for every ``/api/v1/<path>`` request."""
    client = _backend_client()

    path = request.path  # e.g. /api/v1/users/?skip=0&limit=50 (no query)
    stored = session_get(session)

    resp, cookies = forward_request(
        client, request, path=path, bearer_token=stored.access_token or None
    )

    # 401 with a refresh token available -> refresh once and retry.
    if resp.status_code == 401 and stored.refresh_token:
        if _refresh_once(client, _settings()):
            new_stored = session_get(session)
            resp, cookies = forward_request(
                client, request, path=path, bearer_token=new_stored.access_token or None
            )

    _apply_auth_cookies(cookies)
    return resp

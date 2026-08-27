"""Server-side authentication for the BFF.

Login is handled entirely by the BFF:

1. ``POST /auth/login`` authenticates against the backend's password grant, stores the JWTs in a
signed Flask session cookie, mints a one-time auth code (bound to that session), and redirects the
browser to the SPA with ``?code=...``.
2. ``POST /auth/session`` lets the SPA exchange that code for confirmation of who logged in (the
actual credentials already live in the session cookie set by the login redirect).
3. ``GET /auth/me`` returns the current user, silently refreshing the access token first if needed.
4. ``POST /auth/refresh`` forces a token refresh.
5. ``POST /auth/logout`` tells the backend to revoke and clears the session.

The browser never sees a JWT — the BFF injects the access token as an
``Authorization: *** header on every forwarded API call.
"""

from __future__ import annotations

import json
import logging
import secrets
from urllib.parse import quote

from flask import Blueprint, Response, current_app, jsonify, redirect, request, session
from flask.typing import ResponseReturnValue

from app.config import Settings
from app.proxy import forward
from app.security import (
    StoredSession,
    consume_auth_code,
    issue_auth_code,
    session_clear,
    session_get,
    session_set,
)

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

#: Session key holding the per-login ticket that a one-time code is bound to.
_LOGIN_TICKET_KEY = "login_ticket"


def _settings() -> Settings:  # type: ignore[no-untyped-def]
    return current_app.config["SETTINGS"]


def _backend_client():  # type: ignore[no-untyped-def]
    return current_app.config["BACKEND_CLIENT"]


def _read_credentials() -> tuple[str, str]:
    """Extract (username, password) from a form or JSON body."""
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json(silent=True) or {}
        username = data.get("username") or data.get("email") or ""
        password = data.get("password") or ""
    else:
        form = request.form
        username = form.get("username") or form.get("email") or ""
        password = form.get("password") or ""
    return username, password


@auth_bp.post("/login")
def login() -> ResponseReturnValue:
    """Authenticate and redirect to the SPA with a one-time auth code."""
    settings: Settings = _settings()
    client = _backend_client()

    username, password = _read_credentials()
    if not username or not password:
        return jsonify({"detail": "username and password are required"}), 400

    # Forward to the backend's OAuth2 password grant (form-encoded).
    form_body = (
        f"username={quote(username, safe='')}"
        f"&password={quote(password, safe='')}"
        "&scope=api%3Aall"
    ).encode()
    resp, _cookies = forward(
        client,
        method="POST",
        path="/api/v1/login/access-token",
        body=form_body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if resp.status_code != 200:
        # Surface the backend's error verbatim (the SPA reads raw text).
        return Response(resp.get_data(), status=resp.status_code, content_type="application/json")

    try:
        payload = resp.get_json()
    except ValueError:
        return jsonify({"detail": "backend returned an unexpected login response"}), 502

    access_token = payload.get("access_token", "")
    refresh_token = payload.get("refresh_token", "")
    if not access_token:
        return jsonify({"detail": "login did not yield an access token"}), 502

    # Store tokens server-side in the signed session.
    stored = session_get(session)
    stored.access_token = access_token
    stored.refresh_token = refresh_token
    stored.user = {"email": username}
    login_ticket = secrets.token_urlsafe(32)
    session_set(session, stored)
    session[_LOGIN_TICKET_KEY] = login_ticket

    code = issue_auth_code(
        settings.AUTH_CODE_TTL_SECONDS,
        metadata={"ticket": login_ticket, "email": username},
    )
    redirect_url = f"{settings.SPA_URL}/?code={quote(code, safe='')}"

    # ``?redirect=false`` lets a JS client receive the code as JSON (the session
    # cookie is still set on this response) and perform the navigation itself.
    if request.args.get("redirect") == "false":
        return jsonify({"ok": True, "code": code, "redirect_url": redirect_url})

    logger.info("BFF login success for %s; redirecting to SPA", username)
    return redirect(redirect_url)


@auth_bp.post("/session")
def exchange_session() -> ResponseReturnValue:
    """Exchange a one-time auth code for confirmation of the logged-in user."""
    settings: Settings = _settings()
    data = request.get_json(silent=True) or {}
    metadata = consume_auth_code(data.get("code", ""), settings.AUTH_CODE_TTL_SECONDS)

    if metadata is None:
        return jsonify({"detail": "invalid or expired auth code"}), 401

    ticket = session.get(_LOGIN_TICKET_KEY)
    if not ticket or metadata.get("ticket") != ticket:
        # Code is valid but was issued to a different browser session — refuse.
        return jsonify({"detail": "auth code does not match this session"}), 401

    stored = session_get(session)
    session.pop(_LOGIN_TICKET_KEY, None)
    return jsonify({"ok": True, "user": stored.user or {"email": ""}})


@auth_bp.get("/me")
def me() -> ResponseReturnValue:
    """Return the current user, refreshing the access token if needed."""
    settings: Settings = _settings()
    client = _backend_client()

    stored = session_get(session)
    if not stored.authenticated:
        return jsonify({"detail": "Not authenticated"}), 401

    resp, cookies = forward(
        client,
        method="GET",
        path="/api/v1/auth/me",
        headers={"Authorization": f"Bearer {stored.access_token}"},
    )
    if resp.status_code == 401 and stored.refresh_token:
        refreshed = _refresh_tokens(client, settings, stored)
        if refreshed is not None:
            resp, cookies = forward(
                client,
                method="GET",
                path="/api/v1/auth/me",
                headers={"Authorization": f"Bearer {refreshed.access_token}"},
            )

    _apply_auth_cookies(cookies)
    # Keep cached user info fresh from the backend response.
    if resp.status_code == 200:
        try:
            current = session_get(session)
            current.user = resp.get_json() or current.user
            session_set(session, current)
        except ValueError:
            pass
    return Response(resp.get_data(), status=resp.status_code, content_type="application/json")


@auth_bp.post("/refresh")
def refresh() -> ResponseReturnValue:
    """Force a token refresh using the stored refresh token."""
    settings: Settings = _settings()
    client = _backend_client()

    stored = session_get(session)
    if not stored.refresh_token:
        return jsonify({"detail": "no refresh token in session"}), 401

    refreshed = _refresh_tokens(client, settings, stored)
    if refreshed is None:
        return jsonify({"detail": "token refresh failed"}), 401

    session_set(session, refreshed)
    return jsonify({"ok": True, "user": refreshed.user})


@auth_bp.post("/logout")
def logout() -> ResponseReturnValue:
    """Revoke tokens on the backend (best-effort) and clear the session."""
    client = _backend_client()

    stored = session_get(session)
    if stored.authenticated:
        forward(
            client,
            method="POST",
            path="/api/v1/login/logout",
            headers={"Authorization": f"Bearer {stored.access_token}"},
        )  # best-effort; ignore the response

    session_clear(session)
    session.pop(_LOGIN_TICKET_KEY, None)
    return jsonify({"message": "Logged out"})


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #


def _refresh_tokens(client, settings: Settings, stored: StoredSession) -> StoredSession | None:
    """Call the backend refresh endpoint and return an updated session or None."""
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
        return None

    updated = StoredSession(
        access_token=cookies.get("access_token") or "",
        refresh_token=cookies.get("refresh_token") or stored.refresh_token,
        user=stored.user,
    )
    if not updated.access_token:
        # Fall back to the JSON body if no Set-Cookie was present.
        try:
            updated.access_token = resp.get_json().get("access_token", "")
        except ValueError:
            pass
    return updated if updated.access_token else None


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

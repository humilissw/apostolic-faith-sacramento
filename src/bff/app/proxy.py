"""Forwarding to the upstream FastAPI backend.

Hand-rolled with ``httpx`` — no reverse-proxy middleware or tunnel library. The
BFF is a real application layer: it authenticates, injects the access token as
an ``Authorization: *** header, and streams the backend's response back to the
SPA verbatim (status, headers, body).
"""

from __future__ import annotations

import logging
import ssl
from typing import Any
from urllib.parse import urlencode

import httpx
from flask import Response

from app.config import Settings

logger = logging.getLogger(__name__)

#: Request headers that must never be forwarded to the upstream service.
HOP_BY_HOP_REQUEST_HEADERS = {
    "host",
    "content-length",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "accept-encoding",  # we control the request; never ask upstream to compress
}

#: Response headers that must not be copied back to the client.
HOP_BY_HOP_RESPONSE_HEADERS = {
    "content-length",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    # The backend may set token cookies (httpOnly, Secure, SameSite=None). We
    # intentionally do NOT pass these through — the BFF keeps tokens in its own
    # signed session. Passing them would leak JWTs to the browser.
    "set-cookie",
}


def _build_ssl_context(settings: Settings) -> ssl.SSLContext | None:
    """Build an SSL context for talking to the backend.

    * If ``BACKEND_VERIFY`` is on (default): verify against the system CAs, or against
    ``BACKEND_CA_BUNDLE`` when provided. This is what production uses.
    * If verification is off: build an unverified context and log a loud warning. This is
    intended for the self-signed local/dev stack (the backend is reached via the compose
    service name ``backend`` or ``localhost``), matching the convention used by
    ``infrastructure/health_edge.py``.

    Disabling verification is an explicit operator choice (default is on); there is no
    implicit fallback, so a misconfigured remote backend fails loudly at request time
    rather than silently skipping checks.
    """
    if settings.BACKEND_VERIFY:
        return ssl.create_default_context(cafile=settings.BACKEND_CA_BUNDLE)

    logger.warning(
        "BFF is talking to %s with TLS verification DISABLED (self-signed dev cert).",
        settings.BACKEND_URL,
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def build_backend_client(settings: Settings) -> httpx.Client:
    """Create a long-lived ``httpx.Client`` for the upstream backend."""
    verify: Any = True
    if settings.BACKEND_URL.lower().startswith("https://"):
        verify = _build_ssl_context(settings) or False
    return httpx.Client(
        base_url=settings.BACKEND_URL,
        timeout=httpx.Timeout(settings.BACKEND_TIMEOUT),
        verify=verify,
        follow_redirects=False,
        http2=False,
    )


def _filtered_request_headers(
    request, bearer_token: str | None
) -> dict[str, str]:  # type: ignore[no-untyped-def]
    """Copy the incoming request's headers for forwarding, minus hop-by-hop."""
    headers: dict[str, str] = {}
    for key, value in request.headers.items():
        if key.lower() in HOP_BY_HOP_REQUEST_HEADERS:
            continue
        headers[key] = value
    # The BFF is the source of truth for auth toward the backend. Drop any
    # client-supplied Authorization header and inject ours (if authenticated).
    headers.pop("Authorization", None)
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


def forward(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    query_string: bytes = b"",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[Response, dict[str, str]]:
    """Forward a single request to the backend and stream its response back.

    ``path`` must start with ``/`` (e.g. ``/api/v1/users/?limit=5``). Returns a
    ``(response, auth_cookies)`` tuple where ``auth_cookies`` maps the names of
    token cookies found in the upstream ``Set-Cookie`` header to their values
    (empty string when the backend is clearing them). The BFF uses these to keep
    its own session authoritative across token rotation; they are never sent on
    to the browser.

    The returned Flask :class:`Response` mirrors the upstream status code,
    content type, and body exactly so SPA error handling (which reads raw text)
    works unchanged.
    """
    if not path.startswith("/"):
        path = "/" + path

    httpx_request = client.build_request(
        method=method,
        url=path,
        params=query_string.decode("latin-1") if query_string else None,
        content=body,
        headers=headers or {},
    )
    upstream = client.send(httpx_request, stream=True)
    try:
        response_body = upstream.read()
        auth_cookies = _extract_token_cookies(upstream.headers.get_list("set-cookie"))
    finally:
        upstream.close()

    resp = Response(
        response_body,
        status=upstream.status_code,
        content_type=upstream.headers.get("content-type"),
    )
    for key, value in upstream.headers.items():
        if key.lower() in HOP_BY_HOP_RESPONSE_HEADERS:
            continue
        # Content-Length is recomputed by WSGI from the body.
        resp.headers[key] = value
    return resp, auth_cookies


def _extract_token_cookies(set_cookie_headers: list[str]) -> dict[str, str]:
    """Pull ``access_token`` / ``refresh_token`` values out of Set-Cookie headers."""
    captured: dict[str, str] = {}
    wanted = {"access_token", "refresh_token"}
    for header in set_cookie_headers or []:
        first_segment = header.split(";", 1)[0].strip()
        if "=" not in first_segment:
            continue
        name, _, value = first_segment.partition("=")
        if name.strip() in wanted:
            captured[name.strip()] = value.strip()
    return captured


def forward_request(
    client: httpx.Client,
    request,  # type: ignore[no-untyped-def]
    path: str,
    bearer_token: str | None = None,
) -> tuple[Response, dict[str, str]]:
    """Forward the current Flask ``request`` (method/query/body/headers)."""
    # NOTE: never use ``request.data`` here. For form-encoded POST bodies it
    # triggers Werkzeug's form parsing, which consumes the raw stream and then
    # returns empty bytes — the upstream would receive a bodyless request
    # (e.g. the OAuth2 password grant answering 422 "Field required").
    # ``get_data()`` reads/caches the raw stream instead, and the cached copy
    # is still usable by Werkzeug's form parser afterwards.
    body = request.get_data()
    return forward(
        client,
        method=request.method,
        path=path,
        query_string=urlencode(list(request.args.items(multi=True)), doseq=True).encode("latin-1"),
        body=body or None,
        headers=_filtered_request_headers(request, bearer_token),
    )

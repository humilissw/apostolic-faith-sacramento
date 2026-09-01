"""CORS for the BFF.

The SPA is served from its own origin (``SPA_ORIGINS``) and talks to the BFF on
a different port, so cross-origin requests need explicit CORS handling. The BFF
is a same-site cookie host: it sets ``Access-Control-Allow-Credentials: true``
and echoes back the specific requesting origin (never a wildcard, which is
incompatible with credentials).

This is implemented as plain Flask before/after-request hooks — no third-party
CORS package.
"""

from __future__ import annotations

from flask import Response, request


def install_cors(app) -> None:  # type: ignore[no-untyped-def]
    """Register CORS headers for every response on ``app``."""

    @app.after_request
    def _add_cors(response: Response) -> Response:
        origin = request.headers.get("Origin")
        allowed = app.config["SPA_ORIGINS"]
        if origin and origin in allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With"
            )
            max_age = app.config.get("CORS_MAX_AGE", 600)
            response.headers["Access-Control-Max-Age"] = str(max_age)
        return response

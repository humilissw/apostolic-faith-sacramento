"""Flask application factory for the BFF."""

from __future__ import annotations

import atexit
import logging
import secrets

from flask import Flask, Response, jsonify

from app.api import handle_api
from app.auth import auth_bp
from app.config import Settings, load_settings
from app.cors import install_cors
from app.proxy import build_backend_client

logger = logging.getLogger("bff")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_app(settings: Settings | None = None) -> Flask:
    """Build and configure the BFF Flask application."""
    _configure_logging()
    settings = settings or load_settings()

    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    app.config["SPA_ORIGINS"] = set(settings.SPA_ORIGINS)
    app.config["CORS_MAX_AGE"] = 600

    # --- Session (signed cookie; holds JWTs server-side) ------------------- #
    if settings.SECRET_KEY:
        app.secret_key = settings.SECRET_KEY
    else:
        # Local-dev convenience only: a random key means sessions do not
        # survive restarts. Production MUST set SECRET_KEY.
        app.secret_key = secrets.token_hex(32)
        logger.warning("SECRET_KEY is not set — using an ephemeral key (dev only).")

    app.config.update(
        SESSION_COOKIE_NAME=settings.SESSION_COOKIE_NAME,
        SESSION_COOKIE_SECURE=settings.SESSION_COOKIE_SECURE,
        SESSION_COOKIE_SAMESITE=settings.SESSION_COOKIE_SAMESITE,
        SESSION_COOKIE_HTTPONLY=settings.SESSION_COOKIE_HTTPONLY,
        SESSION_COOKIE_PATH="/",
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,  # 7 days
    )

    # --- Upstream backend client ------------------------------------------- #
    client = build_backend_client(settings)
    app.config["BACKEND_CLIENT"] = client
    atexit.register(client.close)

    # --- Blueprints / routes ------------------------------------------------ #
    app.register_blueprint(auth_bp)

    @app.route("/api/v1/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    @app.route("/api/v1/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def api_forward(**_kwargs) -> Response:  # type: ignore[return]
        # The ``<path:path>`` converter injects a ``path`` kwarg; the actual
        # target is read from ``request.path`` inside handle_api().
        return handle_api()

    # --- Service metadata ---------------------------------------------------- #
    @app.route("/")
    def index() -> Response:  # type: ignore[return]
        return jsonify(
            {
                "service": "afc-sacramento-bff",
                "version": "0.1.0",
                "endpoints": {
                    "health": "/health",
                    "login": "POST /auth/login (redirects to SPA with ?code=)",
                    "session": "POST /auth/session {code}",
                    "me": "GET /auth/me",
                    "refresh": "POST /auth/refresh",
                    "logout": "POST /auth/logout",
                    "api": "/api/v1/<path> (forwarded to backend)",
                },
            }
        )

    @app.route("/health")
    def health() -> Response:  # type: ignore[return]
        return jsonify({"status": "ok"})

    # --- CORS ----------------------------------------------------------------- #
    install_cors(app)

    # --- Error handlers (JSON, matching the backend's {"detail": ...} shape) -- #
    @app.errorhandler(404)
    def not_found(_err):  # type: ignore[no-untyped-def]
        return jsonify({"detail": "Not Found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_err):  # type: ignore[no-untyped-def]
        return jsonify({"detail": "Method Not Allowed"}), 405

    @app.errorhandler(500)
    def internal_error(_err):  # type: ignore[no-untyped-def]
        logger.exception("Unhandled BFF error")
        return jsonify({"detail": "Internal Server Error"}), 500

    @app.after_request
    def _security_headers(response: Response) -> Response:
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response

    logger.info(
        "BFF configured: backend=%s spa_origins=%s secure_cookies=%s",
        settings.BACKEND_URL,
        settings.SPA_ORIGINS,
        settings.SESSION_COOKIE_SECURE,
    )
    return app


def main() -> None:
    """Run the BFF over HTTPS (no plain HTTP)."""
    import os

    from werkzeug.serving import run_simple

    settings = load_settings()
    app = create_app(settings)

    host = os.environ.get("BFF_HOST", "0.0.0.0")  # nosec B104 -- container service bind
    port = int(os.environ.get("BFF_PORT", "8002"))
    certfile = os.environ.get("BFF_CERTFILE", "security_keys/cert.pem")
    keyfile = os.environ.get("BFF_KEYFILE", "security_keys/key.pem")

    logger.info("Starting BFF on https://%s:%d (cert=%s)", host, port, certfile)
    run_simple(
        host,
        port,
        app,
        ssl_context=(certfile, keyfile),
        threaded=True,
    )


if __name__ == "__main__":
    main()

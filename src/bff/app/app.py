"""Flask application factory for the BFF."""

from __future__ import annotations

import atexit
import logging
import os
import secrets

from dotenv import load_dotenv
from flask import Flask, Response, jsonify

from app.api import handle_api
from app.auth import auth_bp
from app.config import Settings, load_settings
from app.cors import install_cors
from app.proxy import build_backend_client

load_dotenv()


logger = logging.getLogger("bff")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_app(settings: Settings | None = None) -> Flask:
    try:
        """Build and configure the BFF Flask application."""
        _configure_logging()
        settings = settings or load_settings()
        logging.info("BACKEND_URL", os.getenv("BACKEND_URL", "failure"))
        logging.info("SECRET_KEY", os.getenv("SECRET_KEY", "failure"))
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
            import urllib.request

            try:
                contents = urllib.request.urlopen(
                    os.getenv("BFF_HOST", "failure") + "api/v1/health"
                ).read()
                return jsonify({"status": {"api": contents}})
            except Exception as e:
                print(e)
                logger.error("Failed to get health", e)
                return jsonify({"status": "unhealthy"})

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
    except Exception as e:
        print("Failed to start the BFF application", e)
        logger.error("Failed to start the BFF application", e)


#: Module-level WSGI instance. PaaS hosts (Vercel and friends) import this
#: module expecting a top-level ``app`` Flask object; the factory alone is
#: not enough for their static detection. Settings are read from the
#: environment at import time, which is exactly how those platforms inject
#: configuration.
app = create_app()


def main() -> None:
    """Run the BFF over HTTPS (no plain HTTP)."""
    import os

    from werkzeug.serving import run_simple

    host = os.getenv("BFF_HOST", "0.0.0.0")  # nosec B104 -- container service bind
    port = int(os.getenv("BFF_PORT", "8002"))
    certfile = os.getenv("BFF_CERTFILE", "security_keys/cert.pem")
    keyfile = os.getenv("BFF_KEYFILE", "security_keys/cert_key.pem")

    logger.info("Starting BFF on https://%s:%d (cert=%s)", host, port, certfile)
    run_simple(
        host,
        port,
        app,
        # ssl_context=("adhoc"),
        ssl_context=(certfile, keyfile),
        threaded=True,
    )


if __name__ == "__main__":
    main()

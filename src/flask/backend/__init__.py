from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import settings
from backend.openapi_spec import openapi_bp, _build_spec


def create_app():
    app = Flask(__name__)

    # OpenAPI spec at /api/v1/openapi.json
    @app.route("/api/v1/openapi.json")
    def get_openapi_spec():
        return jsonify(_build_spec())

    cors_origins = settings.BACKEND_CORS_ORIGINS
    if isinstance(cors_origins, str):
        cors_origins = [o.strip() for o in cors_origins.split(",")]

    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["*"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        expose_headers=["*"],
    )

    @app.route("/")
    def read_root():
        return (
            "<html><body><h1>Apostolic Faith Sacramento API</h1></body></html>",
            200,
            {"Content-Type": "text/html"},
        )

    from backend.api.routes import register_routes

    # Register api_root BEFORE blueprints so it takes precedence on GET
    def api_root():
        return jsonify({"status": "ok"}), 200

    app.add_url_rule("/api/v1/", "api_root", api_root, methods=["GET"])
    app.add_url_rule("/api/v1", "api_root_ns", api_root, methods=["GET"])

    register_routes(app)
    app.register_blueprint(openapi_bp)

    from flask import g

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    return app

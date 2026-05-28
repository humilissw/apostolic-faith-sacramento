from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    CORS(
        app,
        origins=[
            "http://localhost.tiangolo.com",
            "https://localhost.tiangolo.com",
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:3000",
            "https://localhost:3000",
            "https://qa.afcsacramento.org",
            "https://pre.afcsacramento.org",
            "https://afcsacramento.org",
            "https://www.afcsacramento.org",
            "https://www.pre.afcsacramento.org",
        ],
        supports_credentials=True,
    )

    from app.api.routes import register_routes

    register_routes(app)

    from flask import g

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    return app

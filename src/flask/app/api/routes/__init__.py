from flask import Flask


def register_routes(app: Flask):
    from app.api.routes import (
        announcements,
        church_services,
        feature_flags,
        health,
        integrations,
        items,
        login,
        media,
        members,
        payments,
        scheduler,
        users,
        utils,
        video_uploads,
    )
    from app.api.routes.client_credentials import router as client_credentials_router
    from app.api.routes.google import router as google_router
    from app.api.routes.private import router as private_router
    from app.api.routes.user_scopes import router as user_scopes_router

    app.register_blueprint(login.router, url_prefix="/api/v1")
    app.register_blueprint(users.router, url_prefix="/api/v1")
    app.register_blueprint(utils.router, url_prefix="/api/v1")
    app.register_blueprint(items.router, url_prefix="/api/v1")
    app.register_blueprint(health.router, url_prefix="/api/v1")
    app.register_blueprint(church_services.router, url_prefix="/api/v1")
    app.register_blueprint(media.router, url_prefix="/api/v1")
    app.register_blueprint(members.router, url_prefix="/api/v1")
    app.register_blueprint(video_uploads.router, url_prefix="/api/v1")
    app.register_blueprint(announcements.router, url_prefix="/api/v1")
    app.register_blueprint(google_router, url_prefix="/api/v1")
    app.register_blueprint(payments.router, url_prefix="/api/v1")
    app.register_blueprint(scheduler.router, url_prefix="/api/v1")
    app.register_blueprint(feature_flags.router, url_prefix="/api/v1")
    app.register_blueprint(client_credentials_router, url_prefix="/api/v1")
    app.register_blueprint(user_scopes_router, url_prefix="/api/v1")
    app.register_blueprint(private_router, url_prefix="/api/v1")
    app.register_blueprint(integrations.router, url_prefix="/api/v1")

from fastapi import APIRouter

from app.api.routes import (
    announcements,
    church_services,
    client_credentials,
    feature_flags,
    google,
    health,
    integrations,
    items,
    login,
    media,
    members,
    payments,
    private,
    scheduler,
    user_scopes,
    users,
    utils,
    video_uploads,
)

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(health.router)
api_router.include_router(church_services.router)
api_router.include_router(media.router)
api_router.include_router(members.router)
api_router.include_router(video_uploads.router)
api_router.include_router(announcements.router)
api_router.include_router(google.router)
api_router.include_router(payments.router)
api_router.include_router(integrations.router)
api_router.include_router(user_scopes.router)
api_router.include_router(client_credentials.router)
api_router.include_router(scheduler.router)
api_router.include_router(feature_flags.router)


api_router.include_router(private.router)

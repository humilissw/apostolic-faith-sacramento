from fastapi import APIRouter

from app.api.routes import (
    announcements,
    church_services,
    health,
    items,
    login,
    media,
    members,
    private,
    users,
    utils,
    video_uploads,
)
from app.config import settings

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


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

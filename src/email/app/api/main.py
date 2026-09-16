from fastapi import APIRouter

from app.api.routes import send

api_router = APIRouter()
api_router.include_router(send.router)

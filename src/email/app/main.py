"""AFC email microservice.

Sends application emails (password-reset, new-user, announcement,
assignment, test) on behalf of the src/be/ backend. Verifies backend-issued
RS256 JWTs (``api:email`` scope required); never issues tokens itself.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.config import settings
from app.core.tracking import init_tracking_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_tracking_db()
    yield


app = FastAPI(
    title="AFC Email Service",
    description=(
        "Email delivery microservice for Apostolic Faith Sacramento. "
        "Send requests require a backend-issued JWT with the api:email scope."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health/", tags=["health"])
async def health() -> dict:
    return {
        "status": "healthy",
        "smtp_configured": settings.smtp_configured,
        "users_db_configured": settings.users_db_configured,
    }

from fastapi import APIRouter

from app.services import church_meeting_service

router = APIRouter(prefix="/church-services", tags=["church-services"])

@router.get("/")
async def health_check() -> str:
    
    return "Healthy"

@router.get("/liveness")
async def health_check() -> str:
    return "Live"

@router.get("/readiness")
async def health_check() -> str:
    return "Ready"

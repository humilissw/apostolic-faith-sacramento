from fastapi import APIRouter

router = APIRouter(prefix="/video-uploads", tags=["video-uploads"])

@router.get("/")
async def health_check() -> str:
    return "Healthy"

@router.get("/liveness")
async def health_check() -> str:
    return "Live"

@router.get("/readiness")
async def health_check() -> str:
    return "Ready"

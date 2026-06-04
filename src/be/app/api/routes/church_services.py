from fastapi import APIRouter

router = APIRouter(prefix="/church-services", tags=["church-services"])


@router.get("/")
async def get_health() -> str:
    return "Healthy"


@router.get("/liveness")
async def get_liveness() -> str:
    return "Live"


@router.get("/readiness")
async def get_readiness() -> str:
    return "Ready"

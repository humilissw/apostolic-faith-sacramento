from typing import List
from flask import request
from app.models import Media
from app.requests.video_request import VideoRequest
from app.responses.add_video_response import AddVideoResponse
from app.services.media_service import MediaService
from fastapi import APIRouter, Response

router = APIRouter(prefix="/media", tags=["media"])
media_service = MediaService()


@router.get("/liveness")
async def health_check() -> str:
    return "Live"


@router.get("/readiness")
async def health_check() -> str:
    return "Ready"


@router.post("/", response_model=None)
async def add_new_media(request: VideoRequest) -> AddVideoResponse:
    response: AddVideoResponse = media_service.add_new_video(request)

    return response


@router.get("/", response_model=AddVideoResponse)
async def get_all_media(request: VideoRequest) -> Response:
    response_body: List[Media] = media_service.get_media(request)

    return Response(response_body, status_code=200)


@router.get("/{media_name}", response_model=AddVideoResponse)
async def get_media(media_name: str) -> AddVideoResponse:

    return response


@router.get("/", response_model=AddVideoResponse)
async def update_media(request: VideoRequest) -> AddVideoResponse:
    response: AddVideoResponse = media_service.add_new_video(request)

    return response


@router.get("/", response_model=AddVideoResponse)
async def update_media(request: VideoRequest) -> AddVideoResponse:
    response: AddVideoResponse = media_service.add_new_video(request)

    return response

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import SessionDep, CurrentUser
from app.crud import (
    create_video_upload,
    get_video_upload,
    get_video_upload_by_id,
    update_video_upload,
    delete_video_upload,
)
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate
from app.responses.video_upload_response import VideoUploadPublic, VideoUploadsPublic
from app.models import Message


router = APIRouter(prefix="/video-uploads", tags=["video-uploads"])


@router.get("/liveness")
async def health_check() -> str:
    """Health check for liveness probe."""
    return "Live"


@router.get("/readiness")
async def health_check() -> str:
    """Health check for readiness probe."""
    return "Ready"


@router.get("/", response_model=VideoUploadsPublic)
async def read_video_uploads(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all video uploads.

    Returns a list of all video uploads with pagination.
    """
    count_statement = select(func.count()).select_from(VideoUpload)
    count_result = await session.execute(count_statement)
    count = count_result.scalar()

    statement = select(VideoUpload).offset(skip).limit(limit)
    result = await session.execute(statement)
    video_uploads = result.scalars().all()

    # Add download URLs (placeholder - should be implemented based on storage)
    video_upload_data = [
        VideoUploadPublicWithUrl(
            id=v.id,
            upload_location=v.upload_location,
            upload_name=v.upload_name,
            created_on=v.created_on,
            updated_on=v.updated_on,
            download_url=f"/video-uploads/{v.id}/download",
        )
        for v in video_uploads
    ]

    return VideoUploadsPublic(data=video_upload_data, count=count)


@router.get("/{video_upload_id}", response_model=VideoUploadPublic)
async def read_video_upload_by_id(
    video_upload_id: str, session: SessionDep
) -> Any:
    """
    Get video upload by ID.

    Returns a single video upload entry by its ID.
    """
    video_upload = await get_video_upload_by_id(session=session, video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
        )

    return VideoUploadPublic(
        id=video_upload.id,
        upload_location=video_upload.upload_location,
        upload_name=video_upload.upload_name,
        created_on=video_upload.created_on,
        updated_on=video_upload.updated_on,
    )


@router.post("/", response_model=VideoUploadPublic, status_code=status.HTTP_201_CREATED)
async def create_video_upload_endpoint(
    *, session: SessionDep, video_upload_in: VideoUploadCreate
) -> Any:
    """
    Create new video upload entry.

    Adds a new video upload entry to the database.
    """
    video_upload = await create_video_upload(session=session, video_upload_in=video_upload_in)
    return VideoUploadPublic(
        id=video_upload.id,
        upload_location=video_upload.upload_location,
        upload_name=video_upload.upload_name,
        created_on=video_upload.created_on,
        updated_on=video_upload.updated_on,
    )


@router.patch("/{video_upload_id}", response_model=VideoUploadPublic)
async def update_video_upload_endpoint(
    *,
    session: SessionDep,
    video_upload_id: str,
    video_upload_in: VideoUploadUpdate,
) -> Any:
    """
    Update a video upload entry.

    Updates an existing video upload entry by ID.
    """
    video_upload = await get_video_upload_by_id(session=session, video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
        )

    video_upload = await update_video_upload(session=session, db_video_upload=video_upload, video_upload_in=video_upload_in)
    return VideoUploadPublic(
        id=video_upload.id,
        upload_location=video_upload.upload_location,
        upload_name=video_upload.upload_name,
        created_on=video_upload.created_on,
        updated_on=video_upload.updated_on,
    )


@router.delete("/{video_upload_id}", response_model=Message)
async def delete_video_upload_endpoint(
    video_upload_id: str, session: SessionDep
) -> Any:
    """
    Delete a video upload entry.

    Deletes a video upload entry by ID.
    """
    video_upload = await get_video_upload_by_id(session=session, video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
        )

    await delete_video_upload(session=session, db_video_upload=video_upload)
    return Message(message="Video upload deleted successfully")


# Helper class for response
class VideoUploadPublicWithUrl(VideoUploadPublic):
    download_url: str | None = None

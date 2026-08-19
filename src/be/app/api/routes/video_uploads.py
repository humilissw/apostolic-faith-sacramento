from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import Message
from app.repositories.video_upload_repo import VideoUploadRepository
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate
from app.responses.video_upload_response import (
    VideoUploadPublic,
    VideoUploadsPublic,
)
from app.services.video_upload_management_service import VideoUploadManagementService

router = APIRouter(prefix="/video-uploads", tags=["video-uploads"])


@router.get("/liveness")
async def health_check() -> str:
    """Health check for liveness probe."""
    return "Live"


@router.get("/readiness")
async def readiness_check() -> str:
    """Health check for readiness probe."""
    return "Ready"


@router.get(
    "/",
    response_model=VideoUploadsPublic,
    dependencies=[require_scope("video_uploads:read")],
)
async def read_video_uploads(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve all video uploads.

    Returns a list of all video uploads with pagination.
    Requires video_uploads:read scope (or superuser).
    """
    svc = VideoUploadManagementService(session)
    video_upload_data, total_count = await svc.get_all_video_uploads(skip=skip, limit=limit)
    return VideoUploadsPublic(data=video_upload_data, count=total_count)


@router.get(
    "/{video_upload_id}",
    response_model=VideoUploadPublic,
    dependencies=[require_scope("video_uploads:read")],
)
async def read_video_upload_by_id(video_upload_id: str, session: SessionDep) -> Any:
    """
    Get video upload by ID.

    Returns a single video upload entry by its ID.
    Requires video_uploads:read scope (or superuser).
    """
    svc = VideoUploadManagementService(session)
    video_upload = await svc.get_video_upload_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
        )
    return video_upload


@router.post(
    "/",
    response_model=VideoUploadPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_scope("video_uploads:manage")],
)
async def create_video_upload_endpoint(
    *,
    session: SessionDep,
    video_upload_in: VideoUploadCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new video upload entry.

    Adds a new video upload entry to the database.
    Requires video_uploads:manage scope (or superuser).
    """
    repository = VideoUploadRepository(session=session)
    video_upload = await repository.create(
        video_upload_in=video_upload_in, owner_id=current_user.id
    )
    return VideoUploadPublic(
        id=video_upload.id,
        upload_location=video_upload.upload_location,
        upload_name=video_upload.upload_name,
        description=video_upload.description,
        reference_text=video_upload.reference_text,
        speaker_name=video_upload.speaker_name,
        media_association_date=video_upload.media_association_date,
        created_on=video_upload.created_on,
        updated_on=video_upload.updated_on,
    )


@router.patch(
    "/{video_upload_id}",
    response_model=VideoUploadPublic,
    dependencies=[require_scope("video_uploads:manage")],
)
async def update_video_upload_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    video_upload_id: str,
    video_upload_in: VideoUploadUpdate,
) -> Any:
    """
    Update a video upload entry.

    Updates an existing video upload entry by ID. Requires ownership or superuser.
    Requires video_uploads:manage scope (or superuser).
    """
    svc = VideoUploadManagementService(session)
    try:
        result = await svc.update_video_upload(video_upload_id, current_user, video_upload_in)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video upload not found",
            )
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete(
    "/{video_upload_id}",
    response_model=Message,
    dependencies=[require_scope("video_uploads:manage")],
)
async def delete_video_upload_endpoint(
    video_upload_id: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete a video upload entry.

    Deletes a video upload entry by ID. Requires ownership or superuser.
    Requires video_uploads:manage scope (or superuser).
    """
    svc = VideoUploadManagementService(session)
    try:
        result = await svc.delete_video_upload(video_upload_id, current_user)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video upload not found",
            )
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

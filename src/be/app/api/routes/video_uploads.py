from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.repositories.video_upload_repo import VideoUploadRepository
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate
from app.responses.video_upload_response import (
    VideoUploadPublic,
    VideoUploadPublicWithUrl,
    VideoUploadsPublic,
)

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
    # dependencies=[require_any_scope(["video_uploads:read", "video_uploads:manage"])],
)
async def read_video_uploads(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve all video uploads.

    Returns a list of all video uploads with pagination.
    """
    repository = VideoUploadRepository(session=session)
    video_uploads, total_count = await repository.get_all(skip=skip, limit=limit)

    # Add download URLs (placeholder - should be implemented based on storage)
    video_upload_data = [
        VideoUploadPublicWithUrl(
            id=v.id,
            upload_location=v.upload_location,
            upload_name=v.upload_name,
            description=v.description,
            reference_text=v.reference_text,
            speaker_name=v.speaker_name,
            media_association_date=v.media_association_date,
            created_on=v.created_on,
            updated_on=v.updated_on,
            download_url=v.upload_location,
        )
        for v in video_uploads
    ]

    return VideoUploadsPublic(data=video_upload_data, count=total_count)


@router.get(
    "/{video_upload_id}",
    response_model=VideoUploadPublic,
    # dependencies=[require_any_scope(["video_uploads:read", "video_uploads:manage"])],
)
async def read_video_upload_by_id(video_upload_id: str, session: SessionDep) -> Any:
    """
    Get video upload by ID.

    Returns a single video upload entry by its ID.
    """
    repository = VideoUploadRepository(session=session)
    video_upload = await repository.get_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
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


@router.post(
    "/",
    response_model=VideoUploadPublic,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[require_any_scope(["video_uploads:write", "video_uploads:manage"])],
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
    Requires authentication.
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
    # dependencies=[require_any_scope(["video_uploads:write", "video_uploads:manage"])],
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

    Updates an existing video upload entry by ID. Requires ownership.
    """
    repository = VideoUploadRepository(session=session)
    video_upload = await repository.get_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
        )
    if current_user.id != video_upload.owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this video upload",
        )

    video_upload = await repository.update(
        db_video_upload=video_upload, video_upload_in=video_upload_in
    )
    return VideoUploadPublic(
        id=video_upload.id,
        upload_location=video_upload.upload_location,
        description=video_upload.description,
        reference_text=video_upload.reference_text,
        speaker_name=video_upload.speaker_name,
        media_association_date=video_upload.media_association_date,
        upload_name=video_upload.upload_name,
        created_on=video_upload.created_on,
        updated_on=video_upload.updated_on,
    )


@router.delete(
    "/{video_upload_id}",
    response_model=Message,
    # dependencies=[require_any_scope(["video_uploads:delete", "video_uploads:manage"])],
)
async def delete_video_upload_endpoint(
    video_upload_id: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete a video upload entry.

    Deletes a video upload entry by ID. Requires ownership.
    """
    repository = VideoUploadRepository(session=session)
    video_upload = await repository.get_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video upload not found",
        )
    if current_user.id != video_upload.owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video upload",
        )

    await repository.delete(db_video_upload=video_upload)
    return Message(message="Video upload deleted successfully")

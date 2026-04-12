import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import SessionDep, CurrentUser
from app.crud import (
    create_media,
    get_media,
    get_media_by_id,
    update_media,
    delete_media,
    get_video_upload_by_id,
)
from app.requests.media_request import MediaCreate, MediaUpdate
from app.responses.media_response import MediaPublic, MediasPublic
from app.models import Message


router = APIRouter(prefix="/media", tags=["media"])


@router.get("/liveness")
async def health_check() -> str:
    """Health check for liveness probe."""
    return "Live"


@router.get("/readiness")
async def health_check() -> str:
    """Health check for readiness probe."""
    return "Ready"


@router.get("/", response_model=MediasPublic)
async def read_media(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all media entries.

    Returns a list of all media entries with pagination.
    """
    count_statement = select(func.count()).select_from(Media)
    count_result = await session.execute(count_statement)
    count = count_result.scalar()

    statement = select(Media).offset(skip).limit(limit)
    result = await session.execute(statement)
    medias = result.scalars().all()

    # Add download URLs (placeholder - should be implemented based on storage)
    media_data = [
        MediaPublicWithUrl(
            id=m.id,
            name=m.name,
            uploaded_on=m.uploaded_on,
            created_on=m.created_on,
            updated_on=m.updated_on,
            download_url=f"/media/{m.id}/download",
        )
        for m in medias
    ]

    return MediasPublic(data=media_data, count=count)


@router.get("/{media_id}", response_model=MediaPublic)
async def read_media_by_id(
    media_id: str, session: SessionDep
) -> Any:
    """
    Get media by ID.

    Returns a single media entry by its ID.
    """
    media = await get_media_by_id(session=session, media_id=media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    return MediaPublic(
        id=media.id,
        name=media.name,
        uploaded_on=media.uploaded_on,
        created_on=media.created_on,
        updated_on=media.updated_on,
    )


@router.post("/", response_model=MediaPublic, status_code=status.HTTP_201_CREATED)
async def create_media_endpoint(
    *, session: SessionDep, media_in: MediaCreate
) -> Any:
    """
    Create new media entry.

    Adds a new media entry to the database.
    """
    media = await create_media(session=session, media_in=media_in)
    return MediaPublic(
        id=media.id,
        name=media.name,
        uploaded_on=media.uploaded_on,
        created_on=media.created_on,
        updated_on=media.updated_on,
    )


@router.patch("/{media_id}", response_model=MediaPublic)
async def update_media_endpoint(
    *,
    session: SessionDep,
    media_id: str,
    media_in: MediaUpdate,
) -> Any:
    """
    Update a media entry.

    Updates an existing media entry by ID.
    """
    media = await get_media_by_id(session=session, media_id=media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    media = await update_media(session=session, db_media=media, media_in=media_in)
    return MediaPublic(
        id=media.id,
        name=media.name,
        uploaded_on=media.uploaded_on,
        created_on=media.created_on,
        updated_on=media.updated_on,
    )


@router.delete("/{media_id}", response_model=Message)
async def delete_media_endpoint(
    media_id: str, session: SessionDep
) -> Any:
    """
    Delete a media entry.

    Deletes a media entry by ID.
    """
    media = await get_media_by_id(session=session, media_id=media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    await delete_media(session=session, db_media=media)
    return Message(message="Media deleted successfully")


# Helper class for response
class MediaPublicWithUrl(MediaPublic):
    download_url: str | None = None

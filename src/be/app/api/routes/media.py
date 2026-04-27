import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func

from app.api.deps import SessionDep
from app.models import Message
from app.repositories.media_repo import MediaRepository
from app.requests.media_request import MediaCreate, MediaUpdate
from app.responses.media_response import MediaPublic, MediasPublic, MediaPublicWithUrl


router = APIRouter(prefix="/media", tags=["media"])
media_service = MediaService()


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
    repository = MediaRepository(session=session)
    medias, total_count = await repository.get_all(skip=skip, limit=limit)

    # Add download URLs (placeholder - should be implemented based on storage)
    media_data = [
        {
            "id": m.id,
            "name": m.name,
            "uploaded_on": m.uploaded_on,
            "created_on": m.created_on,
            "updated_on": m.updated_on,
            "download_url": f"/media/{m.id}/download",
        }
        for m in medias
    ]

    return {"data": media_data, "count": total_count}


@router.get("/{media_id}", response_model=MediaPublic)
async def read_media_by_id(
    media_id: str, session: SessionDep
) -> Any:
    """
    Get media by ID.

    Returns a single media entry by its ID.
    """
    repository = MediaRepository(session=session)
    media = await repository.get_by_id(media_id=media_id)
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
    repository = MediaRepository(session=session)
    media = await repository.create(media_in=media_in)
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
    repository = MediaRepository(session=session)
    media = await repository.get_by_id(media_id=media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    media = await repository.update(db_media=media, media_in=media_in)
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
    repository = MediaRepository(session=session)
    media = await repository.get_by_id(media_id=media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    await repository.delete(db_media=media)
    return Message(message="Media deleted successfully")


# Helper class for response
class MediaPublicWithUrl(MediaPublic):
    download_url: str | None = None

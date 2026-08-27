from typing import Any

from app.services.media_service import MediaService
from app.services.media_management_service import MediaManagementService
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.crud import create_media
from app.models import Message
from app.requests.media_request import MediaCreate, MediaUpdate
from app.responses.media_response import MediaPublic, MediasPublic

router = APIRouter(prefix="/media", tags=["media"])
media_service = MediaService()


@router.get(
    "/",
    response_model=MediasPublic,
)
async def read_media(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve all media entries.

    Returns a list of all media entries with pagination.
    """
    svc = MediaManagementService(session)
    media_data, total_count = await svc.get_all_media(skip=skip, limit=limit)
    return MediasPublic(data=media_data, count=total_count)


@router.get(
    "/{media_id}",
    response_model=MediaPublic,
)
async def read_media_by_id(media_id: str, session: SessionDep) -> Any:
    """
    Get media by ID.

    Returns a single media entry by its ID.
    """
    svc = MediaManagementService(session)
    media = await svc.get_media_by_id(media_id=media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )
    return media


@router.post(
    "/",
    response_model=MediaPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_media_endpoint(
    *, session: SessionDep, current_user: CurrentUser, media_in: MediaCreate
) -> Any:
    """
    Create new media entry.

    Adds a new media entry to the database.
    """
    media = await create_media(session=session, media_in=media_in, owner_id=current_user.id)
    return MediaPublic(
        id=media.id,
        name=media.name,
        uploaded_on=media.uploaded_on,
        created_on=media.created_on,
        updated_on=media.updated_on,
    )


@router.patch(
    "/{media_id}",
    response_model=MediaPublic,
)
async def update_media_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    media_id: str,
    media_in: MediaUpdate,
) -> Any:
    """
    Update a media entry.

    Updates an existing media entry by ID. Requires ownership.
    """
    svc = MediaManagementService(session)
    try:
        result = await svc.update_media(media_id, current_user, media_in)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found",
            )
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete(
    "/{media_id}",
    response_model=Message,
)
async def delete_media_endpoint(
    media_id: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete a media entry.

    Deletes a media entry by ID. Requires ownership.
    """
    svc = MediaManagementService(session)
    try:
        result = await svc.delete_media(media_id, current_user)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found",
            )
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

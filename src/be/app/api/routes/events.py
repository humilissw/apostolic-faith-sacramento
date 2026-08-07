from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import Event, Message
from app.repositories.event_repo import EventRepository
from app.requests.event_request import EventCreate, EventUpdate
from app.responses.event_response import EventPublic, EventsPublic

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/liveness")
async def get_liveness() -> str:
    """Health check for liveness probe."""
    return "Live"


@router.get("/readiness")
async def get_readiness() -> str:
    """Health check for readiness probe."""
    return "Ready"


@router.get(
    "/",
    response_model=EventsPublic,
    dependencies=[require_scope("superuser")],
)
async def read_events(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve all event entries.

    Returns a list of all event entries with pagination.
    """
    repository = EventRepository(session=session)
    events, total_count = await repository.get_all(skip=skip, limit=limit)

    return EventsPublic(
        data=[EventPublic.model_validate(i.model_dump()) for i in events], 
        count=total_count)


@router.get(
    "/{event_id}",
    response_model=EventPublic,
    dependencies=[require_scope("api:all")],
)
async def read_event_by_id(event_id: str, session: SessionDep) -> Any:
    """
    Get event by ID.

    Returns a single event entry by its ID.
    """
    repository = EventRepository(session=session)
    event = await repository.get_by_id(event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventPublic(
        id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        created_on=event.created_on,
        updated_on=event.updated_on,
        #uploaded_on=event.uploaded_on,
    )


@router.post(
    "/",
    response_model=EventPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_scope("api:all")],
)
async def create_event_endpoint(
    *, session: SessionDep, event_in: EventCreate
) -> Any:
    """
    Create new event entry.

    Adds a new event entry to the database.
    """
    repository = EventRepository(session=session)
    event = await repository.create(event_in=event_in)
    return EventPublic(
        id=event.id,
        title=event.title,
        date=event.date,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        created_on=event.created_on,
        updated_on=event.updated_on,
        #uploaded_on=event.uploaded_on,
    )


@router.patch(
    "/{event_id}",
    response_model=EventPublic,
    dependencies=[require_scope("api:all")],
)
async def update_event_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: str,
    event_in: EventUpdate,
) -> Any:
    """
    Update an event entry.

    Updates an existing event entry by ID. Requires ownership.
    """
    repository = EventRepository(session=session)
    event = await repository.get_by_id(event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    if current_user.id != event.owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this event",
        )

    event = await repository.update(db_event=event, event_in=event_in)
    return EventPublic(
        id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        created_on=event.created_on,
        updated_on=event.updated_on,
        #uploaded_on=event.uploaded_on,

    )


@router.delete(
    "/{event_id}",
    response_model=Message,
    dependencies=[require_scope("api:all")],
)
async def delete_event_endpoint(
    event_id: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete an event entry.

    Deletes an event entry by ID. Requires ownership.
    """
    repository = EventRepository(session=session)
    event = await repository.get_by_id(event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    if current_user.id != event.owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this event",
        )

    await repository.delete(db_event=event)
    return Message(message="Event deleted successfully")
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event
from app.requests.event_request import EventCreate, EventUpdate


class EventRepository:
    """
    Repository for Event entity operations.
    Handles all database interactions for event entries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, event_in: EventCreate) -> Event:
        """
        Create a new event entry.

        Args:
            event_in: EventCreate object containing event data

        Returns:
            Event: Created event object
        """
        db_obj = Event(
            title=event_in.title,
            description=event_in.description,
            date=event_in.date,
            start_time=event_in.start_time,
            end_time=event_in.end_time,
            created_on=datetime.now(UTC),
            updated_on=datetime.now(UTC),
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj  # type: ignore[no-any-return]

    async def get_by_id(self, event_id: int | str) -> Event | None:
        """
        Retrieve an event entry by id or new_id.
        """
        statement = select(Event).where(Event.id == event_id)  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        event = result.scalar_one_or_none()
        if event:
            return event  # type: ignore[no-any-return]
        statement = select(Event).where(Event.id == str(event_id))  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Event], int]:
        """
        Retrieve all event entries with pagination.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)

        Returns:
            tuple[list[Event], int]: Tuple of (events list, total count)
        """
        # Get total count
        count_statement = select(func.count()).select_from(Event)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar()
        print("making it here?")

        # Get paginated results
        statement = select(Event).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        events = result.scalars().all()

        return list(events), total_count or 0

    async def update(self, db_event: Event, event_in: EventUpdate) -> Event:
        """
        Update an existing event entry.

        Args:
            db_event: Event object to update
            event_in: EventUpdate object with update data

        Returns:
            Event: Updated event object
        """
        event_data = event_in.model_dump(exclude_unset=True)
        db_event.sqlmodel_update(event_data)
        self.session.add(db_event)
        await self.session.commit()
        await self.session.refresh(db_event)
        return db_event

    async def delete(self, db_event: Event) -> None:
        """
        Delete an event entry.

        Args:
            db_event: Event object to delete
        """
        await self.session.delete(db_event)
        await self.session.commit()

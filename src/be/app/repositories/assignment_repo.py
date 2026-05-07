from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Assignment
from app.requests.assignment_request import AssignmentCreate, AssignmentUpdate
from datetime import datetime, timezone


class AssignmentRepository:
    """Repository for Assignment entity operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, assignment_in: AssignmentCreate) -> Assignment:
        assignment = Assignment(
            user_id=assignment_in.user_id,
            event_date=assignment_in.event_date,
            type=assignment_in.type,
            role=assignment_in.role,
            instrument=assignment_in.instrument,
            notes=assignment_in.notes,
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )
        self.session.add(assignment)
        await self.session.commit()
        await self.session.refresh(assignment)
        return assignment

    async def get_by_id(self, assignment_id: str) -> Assignment | None:
        statement = select(Assignment).where(
            Assignment.id == assignment_id  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Assignment], int]:
        count_statement = select(func.count()).select_from(Assignment)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar()
        statement = select(Assignment).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all()), total_count or 0

    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list[Assignment]:
        statement = (
            select(Assignment)
            .where(Assignment.event_date >= start_date)  # type: ignore[arg-type]
            .where(Assignment.event_date <= end_date)  # type: ignore[arg-type]
            .order_by(Assignment.event_date)  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: str) -> list[Assignment]:
        statement = select(Assignment).where(
            Assignment.user_id == user_id  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update(
        self, db_assignment: Assignment, assignment_in: AssignmentUpdate
    ) -> Assignment:
        update_data = assignment_in.model_dump(exclude_unset=True)
        update_data["updated_on"] = datetime.now(timezone.utc)
        if "created_on" in update_data:
            del update_data["created_on"]
        db_assignment.sqlmodel_update(update_data)
        self.session.add(db_assignment)
        await self.session.commit()
        await self.session.refresh(db_assignment)
        return db_assignment

    async def delete(self, db_assignment: Assignment) -> None:
        await self.session.delete(db_assignment)
        await self.session.commit()

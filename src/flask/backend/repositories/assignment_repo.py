from pydantic import BaseModel
from sqlalchemy import select, func
from backend.models import Assignment
from backend.requests.assignment_request import AssignmentCreate, AssignmentUpdate
from datetime import datetime, timezone


class AssignmentConflict(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    type: str
    role: str
    event_date: datetime


class AssignmentRepository:
    def __init__(self, session):
        self.session = session

    def check_conflicts(self, user_id: str, event_date: datetime, assignment_id: str | None = None) -> list[AssignmentConflict]:
        stmt = (
            select(Assignment)
            .where(Assignment.user_id == user_id)
            .where(Assignment.event_date >= event_date.replace(hour=0, minute=0, second=0))
            .where(Assignment.event_date < event_date.replace(hour=23, minute=59, second=59))
        )
        if assignment_id:
            stmt = stmt.where(Assignment.id != assignment_id)
        result = self.session.execute(stmt)
        conflicts = result.scalars().all()
        return [
            AssignmentConflict(
                id=a.id,
                type=a.type.value if hasattr(a.type, "value") else str(a.type),
                role=a.role,
                event_date=a.event_date,
            )
            for a in conflicts
        ]

    def create(self, assignment_in: AssignmentCreate) -> Assignment | None:
        try:
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
            self.session.commit()
            self.session.refresh(assignment)
            return assignment
        except Exception as err:
            print(err)
            self.session.rollback()
            return None

    def get_by_id(self, assignment_id: str) -> Assignment | None:
        statement = select(Assignment).where(Assignment.id == assignment_id)
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Assignment], int]:
        count_statement = select(func.count()).select_from(Assignment)
        count_result = self.session.execute(count_statement)
        total_count = count_result.scalar()
        statement = select(Assignment).offset(skip).limit(limit)
        result = self.session.execute(statement)
        return list(result.scalars().all()), total_count or 0

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list[Assignment]:
        statement = (
            select(Assignment).where(Assignment.event_date >= start_date).where(Assignment.event_date <= end_date).order_by(Assignment.event_date)
        )
        result = self.session.execute(statement)
        return list(result.scalars().all())

    def get_by_user_id(self, user_id: str) -> list[Assignment]:
        statement = select(Assignment).where(Assignment.user_id == user_id)
        result = self.session.execute(statement)
        return list(result.scalars().all())

    def get_by_user_and_date_range(self, user_id: str, start_date: datetime, end_date: datetime) -> list[Assignment]:
        statement = (
            select(Assignment)
            .where(Assignment.user_id == user_id)
            .where(Assignment.event_date >= start_date)
            .where(Assignment.event_date <= end_date)
            .order_by(Assignment.event_date)
        )
        result = self.session.execute(statement)
        return list(result.scalars().all())

    def update(self, db_assignment: Assignment, assignment_in: AssignmentUpdate) -> Assignment:
        update_data = assignment_in.model_dump(exclude_unset=True)
        update_data["updated_on"] = datetime.now(timezone.utc)
        if "created_on" in update_data:
            del update_data["created_on"]
        db_assignment.sqlmodel_update(update_data)
        self.session.add(db_assignment)
        self.session.commit()
        self.session.refresh(db_assignment)
        return db_assignment

    def delete(self, db_assignment: Assignment) -> None:
        self.session.delete(db_assignment)
        self.session.commit()

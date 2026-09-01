"""Service for assignment management operations."""

from datetime import datetime

from app.models import AssignmentPublic, User
from app.repositories.assignment_repo import AssignmentRepository
from app.requests.assignment_request import AssignmentCreate, AssignmentUpdate
from app.services.scheduler_service import SchedulerService


class AssignmentService:
    """Handles business logic for assignment CRUD and bulk operations."""

    def __init__(self, session):
        self.session = session

    async def get_by_user_id(self, user_id: str) -> list:
        """Get assignments for a specific user."""
        repo = AssignmentRepository(session=self.session)
        return await repo.get_by_user_id(user_id)

    async def get_by_date_range(self, start: datetime, end: datetime) -> list:
        """Get assignments within a date range."""
        repo = AssignmentRepository(session=self.session)
        return await repo.get_by_date_range(start, end)

    async def get_by_user_and_date_range(
        self, user_id: str, start: datetime, end: datetime
    ) -> list:
        """Get assignments for a user within a date range."""
        repo = AssignmentRepository(session=self.session)
        return await repo.get_by_user_and_date_range(user_id, start, end)

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        """Get all assignments with pagination."""
        repo = AssignmentRepository(session=self.session)
        return await repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, assignment_id: str):
        """Get a single assignment by ID."""
        repo = AssignmentRepository(session=self.session)
        return await repo.get_by_id(assignment_id)

    async def enrich_assignments_with_user_data(self, assignments: list) -> list:
        """Enrich assignments with user email and full name."""
        enriched = []
        for a in assignments:
            user = await self.session.get(User, a.user_id)
            enriched.append(
                {
                    **AssignmentPublic.model_validate(a).model_dump(),
                    "user_email": user.email if user else "unknown",
                    "user_full_name": (
                        user.full_name
                        if user and user.full_name
                        else (user.email if user else "unknown")
                    ),
                }
            )
        return enriched

    async def check_conflicts(self, user_id: str, event_date: datetime) -> list:
        """Check for scheduling conflicts for a user on a given date."""
        repo = AssignmentRepository(session=self.session)
        return await repo.check_conflicts(user_id=user_id, event_date=event_date)

    async def create_assignment(
        self, assignment_in: AssignmentCreate
    ) -> tuple[AssignmentPublic | None, list]:
        """Create a single assignment with conflict checking.

        Returns (assignment_or_none, conflicts_list).
        """
        repo = AssignmentRepository(session=self.session)

        # Check for double-booking conflicts
        conflicts = await repo.check_conflicts(
            user_id=assignment_in.user_id,
            event_date=assignment_in.event_date,
        )
        if conflicts:
            return None, conflicts

        assignment = await repo.create(assignment_in=assignment_in)
        if assignment is None:
            return None, []

        # Send email notification
        scheduler_svc = SchedulerService(self.session)
        await scheduler_svc.send_assignment_notification(
            user_id=assignment.user_id,
            assignment_type=assignment_in.type.value,
            role=assignment_in.role,
            event_date=assignment.event_date.strftime("%B %d, %Y"),
            instrument=assignment_in.instrument,
            notes=assignment_in.notes,
        )

        return AssignmentPublic.model_validate(assignment), []

    async def update_assignment(self, assignment_id: str, assignment_in: AssignmentUpdate):
        """Update an existing assignment."""
        repo = AssignmentRepository(session=self.session)
        assignment = await repo.get_by_id(assignment_id)
        if not assignment:
            return None
        return await repo.update(db_assignment=assignment, assignment_in=assignment_in)

    async def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment. Returns True if deleted, False if not found."""
        repo = AssignmentRepository(session=self.session)
        assignment = await repo.get_by_id(assignment_id)
        if not assignment:
            return False
        await repo.delete(db_assignment=assignment)
        return True

    async def bulk_assign(self, entries: list, event_date: datetime, type) -> tuple[list, list]:
        """Bulk create assignments with conflict checking and notifications.

        Returns (created_list, conflicts_list).
        """
        repo = AssignmentRepository(session=self.session)
        scheduler_svc = SchedulerService(self.session)

        created = []
        conflicts = []

        for entry in entries:
            assignment_in = AssignmentCreate(
                user_id=entry.user_id,
                event_date=event_date,
                type=type,
                role=entry.role,
                instrument=entry.instrument,
                notes=entry.notes,
                group_leader=entry.group_leader,
            )

            # Check for double-booking conflicts
            conflicts_check = await repo.check_conflicts(
                user_id=entry.user_id,
                event_date=event_date,
            )
            if conflicts_check:
                conflicts.append(
                    {
                        "user_id": entry.user_id,
                        "message": (
                            f"User already has an assignment on "
                            f"{event_date.strftime('%Y-%m-%d')}"
                        ),
                        "conflicts": [c.model_dump() for c in conflicts_check],
                    }
                )
                continue

            assignment = await repo.create(assignment_in=assignment_in)
            if assignment is None:
                conflicts.append(
                    {
                        "user_id": entry.user_id,
                        "message": "Failed to create assignment",
                    }
                )
                continue

            # Send email notification
            await scheduler_svc.send_assignment_notification(
                user_id=assignment.user_id,
                assignment_type=type.value,
                role=entry.role,
                event_date=assignment.event_date.strftime("%B %d, %Y"),
                instrument=entry.instrument,
                notes=entry.notes,
            )

            created.append(AssignmentPublic.model_validate(assignment))

        return created, conflicts

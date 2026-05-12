"""Routes for scheduler assignment management."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import (
    AssignmentPublic,
    AssignmentsPublic,
    TimeOffRequestPublic,
    TimeOffRequest,
    TimeOffRequestStatus,
    User,
)
from app.requests.assignment_request import (
    AssignmentCreate,
    AssignmentUpdate,
    BulkAssignRequest,
    TimeOffRequestCreate,
)
from app.repositories.assignment_repo import AssignmentRepository
from app.services.scheduler_service import SchedulerService
from sqlmodel import select

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


class TimeOffRequestsPublic(BaseModel):
    data: list[TimeOffRequestPublic]
    count: int


class EnrichedAssignment(AssignmentPublic):
    user_email: str
    user_full_name: str | None


class EnrichedAssignmentsResponse(BaseModel):
    data: list[EnrichedAssignment]
    count: int


# ── Time-off request routes ──────────────────────────────────────────


@router.get(
    "/time-off-requests",
    response_model=TimeOffRequestsPublic,
    dependencies=[require_scope("member:limited")],
)
async def get_my_time_off(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
    end_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
) -> Any:
    """Get current user's time-off requests (member:limited scope required)."""
    stmt = select(TimeOffRequest).where(TimeOffRequest.user_id == current_user.id)
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        stmt = stmt.where(TimeOffRequest.date >= start)
        stmt = stmt.where(TimeOffRequest.date <= end)
    stmt = stmt.order_by(TimeOffRequest.date)  # type: ignore[arg-type]
    result = await session.execute(stmt)
    items = result.scalars().all()
    return TimeOffRequestsPublic(
        data=[TimeOffRequestPublic.model_validate(a) for a in items],
        count=len(items),
    )


@router.post(
    "/time-off-request",
    response_model=TimeOffRequestPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_scope("member:limited")],
)
async def create_time_off_request(
    session: SessionDep,
    current_user: CurrentUser,
    data: TimeOffRequestCreate = ...,  # type: ignore[assignment]
) -> Any:
    """Create a time-off request for the current user."""
    row = TimeOffRequest(
        user_id=current_user.id,
        date=data.date,
        status=TimeOffRequestStatus.pending,
        notes=data.notes,
        created_on=datetime.now(timezone.utc),
        updated_on=None,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return TimeOffRequestPublic.model_validate(row)


@router.patch(
    "/time-off-requests/{time_off_id}/approve",
    response_model=TimeOffRequestPublic,
    dependencies=[require_scope("scheduler:admin")],
)
async def approve_time_off_request(
    time_off_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Approve a time-off request (admin only)."""
    row = await session.get(TimeOffRequest, time_off_id)
    if not row:
        raise HTTPException(status_code=404, detail="Time-off request not found")
    row.status = TimeOffRequestStatus.approved
    row.updated_on = datetime.now(timezone.utc)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return TimeOffRequestPublic.model_validate(row)


@router.patch(
    "/time-off-requests/{time_off_id}/decline",
    response_model=TimeOffRequestPublic,
    dependencies=[require_scope("scheduler:admin")],
)
async def decline_time_off_request(
    time_off_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Decline a time-off request (admin only)."""
    row = await session.get(TimeOffRequest, time_off_id)
    if not row:
        raise HTTPException(status_code=404, detail="Time-off request not found")
    row.status = TimeOffRequestStatus.declined
    row.updated_on = datetime.now(timezone.utc)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return TimeOffRequestPublic.model_validate(row)


@router.delete(
    "/time-off-requests/{time_off_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_scope("member:limited")],
)
async def delete_time_off_request(
    time_off_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Delete a time-off request (owner only)."""
    row = await session.get(TimeOffRequest, time_off_id)
    if not row:
        raise HTTPException(status_code=404, detail="Time-off request not found")
    if row.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own time-off requests")
    await session.delete(row)
    await session.commit()


# ── Assignment routes ──────────────────────────────────────


@router.get(
    "/my-assignments",
    response_model=AssignmentsPublic,
    dependencies=[require_scope("member:limited")],
)
async def get_my_assignments(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Get current user's own assignments (member:limited scope required)."""
    repo = AssignmentRepository(session=session)
    assignments = await repo.get_by_user_id(current_user.id)
    return AssignmentsPublic(
        data=[AssignmentPublic.model_validate(a) for a in assignments],
        count=len(assignments),
    )


@router.get(
    "/calendar",
    response_model=AssignmentsPublic,
    dependencies=[require_scope("member:limited")],
)
async def get_calendar_assignments(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: str = Query(..., description="ISO date YYYY-MM-DD"),
    end_date: str = Query(..., description="ISO date YYYY-MM-DD"),
) -> Any:
    """Get assignments for a date range (member:limited scope required)."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    repo = AssignmentRepository(session=session)
    assignments = await repo.get_by_date_range(start, end)
    return AssignmentsPublic(
        data=[AssignmentPublic.model_validate(a) for a in assignments],
        count=len(assignments),
    )


@router.get(
    "/calendar-with-names",
    response_model=EnrichedAssignmentsResponse,
    dependencies=[require_scope("member:limited")],
)
async def get_calendar_with_names(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: str = Query(..., description="ISO date YYYY-MM-DD"),
    end_date: str = Query(..., description="ISO date YYYY-MM-DD"),
) -> Any:
    """Get assignments for a date range, including user email (member:limited scope required)."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    repo = AssignmentRepository(session=session)
    assignments = await repo.get_by_date_range(start, end)
    enriched: list[EnrichedAssignment] = []
    for a in assignments:
        user = await session.get(User, a.user_id)
        enriched.append(
            EnrichedAssignment(
                **AssignmentPublic.model_validate(a).model_dump(),
                user_email=user.email if user else "unknown",
                user_full_name=(
                    user.full_name
                    if user and user.full_name
                    else (user.email if user else "unknown")
                ),
            )
        )
    return EnrichedAssignmentsResponse(data=enriched, count=len(enriched))


@router.get(
    "/my-calendar",
    response_model=AssignmentsPublic,
    dependencies=[require_scope("member:limited")],
)
async def get_my_calendar(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: str = Query(..., description="ISO date YYYY-MM-DD"),
    end_date: str = Query(..., description="ISO date YYYY-MM-DD"),
) -> Any:
    """Get current user's own assignments in a date range (member:limited scope required)."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    repo = AssignmentRepository(session=session)
    assignments = await repo.get_by_user_and_date_range(current_user.id, start, end)
    return AssignmentsPublic(
        data=[AssignmentPublic.model_validate(a) for a in assignments],
        count=len(assignments),
    )


@router.get(
    "/",
    response_model=AssignmentsPublic,
    dependencies=[require_scope("scheduler:admin")],
)
async def list_assignments(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all assignments (scheduler:admin scope required)."""
    repo = AssignmentRepository(session=session)
    assignments, total_count = await repo.get_all(skip=skip, limit=limit)
    return AssignmentsPublic(
        data=[AssignmentPublic.model_validate(a) for a in assignments],
        count=total_count,
    )


@router.get(
    "/{assignment_id}",
    response_model=AssignmentPublic,
    dependencies=[require_scope("scheduler:admin")],
)
async def get_assignment(
    assignment_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Get a single assignment (scheduler:admin scope required)."""
    repo = AssignmentRepository(session=session)
    assignment = await repo.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return AssignmentPublic.model_validate(assignment)


@router.post(
    "/",
    response_model=AssignmentPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_scope("scheduler:admin")],
)
async def create_assignment(
    session: SessionDep,
    current_user: CurrentUser,
    assignment_in: AssignmentCreate = ...,  # type: ignore[assignment]
) -> Any:
    """Create a new assignment (scheduler:admin scope required)."""
    repo = AssignmentRepository(session=session)

    # Check for double-booking conflicts
    conflicts = await repo.check_conflicts(
        user_id=assignment_in.user_id,
        event_date=assignment_in.event_date,
    )
    if conflicts:
        conflict_ids = [c.id for c in conflicts]
        conflict_details = "\n".join(
            f"  - {c.type}: {c.role} on {c.event_date.strftime('%Y-%m-%d')}" for c in conflicts
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "User already has an assignment on this date.",
                "conflicts": [c.model_dump() for c in conflicts],
                "conflict_ids": conflict_ids,
                "details": conflict_details,
            },
        )

    assignment = await repo.create(assignment_in=assignment_in)
    if assignment is None:
        raise HTTPException(status_code=500, detail="Failed to create assignment")

    # Send email notification
    scheduler_svc = SchedulerService(session)
    await scheduler_svc.send_assignment_notification(
        user_id=assignment.user_id,
        assignment_type=assignment_in.type.value,
        role=assignment_in.role,
        event_date=assignment.event_date.strftime("%B %d, %Y"),
        instrument=assignment_in.instrument,
        notes=assignment_in.notes,
    )

    return AssignmentPublic.model_validate(assignment)


@router.patch(
    "/{assignment_id}",
    response_model=AssignmentPublic,
    dependencies=[require_scope("scheduler:admin")],
)
async def update_assignment(
    assignment_id: str,
    session: SessionDep,
    current_user: CurrentUser,
    assignment_in: AssignmentUpdate = ...,  # type: ignore[assignment]
) -> Any:
    """Update an assignment (scheduler:admin scope required)."""
    repo = AssignmentRepository(session=session)
    assignment = await repo.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment = await repo.update(db_assignment=assignment, assignment_in=assignment_in)
    return AssignmentPublic.model_validate(assignment)


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_scope("scheduler:admin")],
)
async def delete_assignment(
    assignment_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Delete an assignment (scheduler:admin scope required)."""
    repo = AssignmentRepository(session=session)
    assignment = await repo.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await repo.delete(db_assignment=assignment)


class BulkAssignResponse(BaseModel):
    created: list[AssignmentPublic]
    conflicts: list[dict[str, Any]]


@router.post(
    "/bulk",
    response_model=BulkAssignResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_scope("scheduler:admin")],
)
async def bulk_assign(
    session: SessionDep,
    current_user: CurrentUser,
    bulk_in: BulkAssignRequest,
) -> Any:
    """Bulk create assignments for multiple users on the same date
    (scheduler:admin scope required)."""
    repo = AssignmentRepository(session=session)
    scheduler_svc = SchedulerService(session)

    created: list[AssignmentPublic] = []
    conflicts: list[dict[str, Any]] = []

    for entry in bulk_in.entries:
        assignment_in = AssignmentCreate(
            user_id=entry.user_id,
            event_date=bulk_in.event_date,
            type=bulk_in.type,
            role=entry.role,
            instrument=entry.instrument,
            notes=entry.notes,
            group_leader=entry.group_leader,
        )

        # Check for double-booking conflicts
        conflicts_check = await repo.check_conflicts(
            user_id=entry.user_id,
            event_date=bulk_in.event_date,
        )
        if conflicts_check:
            conflicts.append(
                {
                    "user_id": entry.user_id,
                    "message": "User already has an assignment on "
                    + f"{bulk_in.event_date.strftime('%Y-%m-%d')}",
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
            assignment_type=bulk_in.type.value,
            role=entry.role,
            event_date=assignment.event_date.strftime("%B %d, %Y"),
            instrument=entry.instrument,
            notes=entry.notes,
        )

        created.append(AssignmentPublic.model_validate(assignment))

    return BulkAssignResponse(created=created, conflicts=conflicts)

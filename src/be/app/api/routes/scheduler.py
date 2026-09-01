"""Routes for scheduler assignment management."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import (
    AssignmentPublic,
    AssignmentsPublic,
    TimeOffRequestPublic,
)
from app.requests.assignment_request import (
    AssignmentCreate,
    AssignmentUpdate,
    BulkAssignRequest,
    TimeOffRequestCreate,
)
from app.services.assignment_service import AssignmentService
from app.services.time_off_request_service import TimeOffRequestService

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
    svc = TimeOffRequestService(session)
    items = await svc.get_user_time_off(current_user.id, start_date, end_date)
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
    svc = TimeOffRequestService(session)
    row = await svc.create_time_off_request(
        user_id=current_user.id,
        date=data.date,
        notes=data.notes,
    )
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
    svc = TimeOffRequestService(session)
    try:
        row = await svc.approve_request(time_off_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
    svc = TimeOffRequestService(session)
    try:
        row = await svc.decline_request(time_off_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
    svc = TimeOffRequestService(session)
    try:
        await svc.delete_request(time_off_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    svc = AssignmentService(session)
    assignments = await svc.get_by_user_id(current_user.id)
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
    svc = AssignmentService(session)
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    assignments = await svc.get_by_date_range(start, end)
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
    svc = AssignmentService(session)
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    assignments = await svc.get_by_date_range(start, end)
    enriched = await svc.enrich_assignments_with_user_data(assignments)
    return EnrichedAssignmentsResponse(
        data=[EnrichedAssignment(**e) for e in enriched],  # type: ignore[arg-type]
        count=len(enriched),
    )


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
    svc = AssignmentService(session)
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    assignments = await svc.get_by_user_and_date_range(current_user.id, start, end)
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
    svc = AssignmentService(session)
    assignments, total_count = await svc.get_all(skip=skip, limit=limit)
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
    svc = AssignmentService(session)
    assignment = await svc.get_by_id(assignment_id)
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
    svc = AssignmentService(session)

    assignment, conflicts = await svc.create_assignment(assignment_in)
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

    if assignment is None:
        raise HTTPException(status_code=500, detail="Failed to create assignment")

    return assignment


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
    svc = AssignmentService(session)
    result = await svc.update_assignment(assignment_id, assignment_in)
    if not result:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return AssignmentPublic.model_validate(result)


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
    svc = AssignmentService(session)
    deleted = await svc.delete_assignment(assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found")


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
    svc = AssignmentService(session)

    created, conflicts = await svc.bulk_assign(
        entries=bulk_in.entries,
        event_date=bulk_in.event_date,
        type=bulk_in.type,
    )

    return BulkAssignResponse(created=created, conflicts=conflicts)

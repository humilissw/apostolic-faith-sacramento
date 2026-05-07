"""Routes for scheduler assignment management."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import AssignmentPublic, AssignmentsPublic
from app.requests.assignment_request import AssignmentCreate, AssignmentUpdate
from app.repositories.assignment_repo import AssignmentRepository

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


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


@router.get("/", response_model=AssignmentsPublic, dependencies=[require_scope("scheduler:admin")])
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
    assignment = await repo.create(assignment_in=assignment_in)
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

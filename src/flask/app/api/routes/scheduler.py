"""Routes for scheduler assignment management."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel
from flask import Blueprint, jsonify, request

from app.models import TimeOffRequestPublic

from app.api.deps import (
    get_current_user,
    get_current_active_superuser,
    get_db,
    require_scope,
)
from app.models import (
    AssignmentPublic,
    AssignmentsPublic,
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
from sqlalchemy import select

router = Blueprint("scheduler", __name__, url_prefix="/scheduler")


class TimeOffRequestsPublic(BaseModel):
    data: list[TimeOffRequestPublic]
    count: int


class EnrichedAssignment(AssignmentPublic):
    user_email: str
    user_full_name: str | None


class EnrichedAssignmentsResponse(BaseModel):
    data: list[EnrichedAssignment]
    count: int


# ── Time-off request routes ──────────


@router.route("/time-off-requests", methods=["GET"])
@require_scope("member:limited")
def get_my_time_off(start_date: str = None, end_date: str = None):
    session = get_db()
    current_user = get_current_user()
    stmt = select(TimeOffRequest).where(TimeOffRequest.user_id == current_user.id)
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        stmt = stmt.where(TimeOffRequest.date >= start).where(TimeOffRequest.date <= end)
    stmt = stmt.order_by(TimeOffRequest.date)
    result = session.execute(stmt)
    items = result.scalars().all()
    return jsonify(
        TimeOffRequestsPublic(
            data=[TimeOffRequestPublic.model_validate(a) for a in items], count=len(items)
        ).model_dump()
    )


@router.route("/time-off-request", methods=["POST"])
@require_scope("member:limited")
def create_time_off_request():
    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    data_request = TimeOffRequestCreate(**data)
    row = TimeOffRequest(
        user_id=current_user.id,
        date=data_request.date,
        status=TimeOffRequestStatus.pending,
        notes=data_request.notes,
        created_on=datetime.now(timezone.utc),
        updated_on=None,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return jsonify(TimeOffRequestPublic.model_validate(row).model_dump()), 201


@router.route("/time-off-requests/<time_off_id>/approve", methods=["PATCH"])
@require_scope("scheduler:admin")
def approve_time_off_request(time_off_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    row = session.get(TimeOffRequest, time_off_id)
    if not row:
        return jsonify({"detail": "Time-off request not found"}), 404
    row.status = TimeOffRequestStatus.approved
    row.updated_on = datetime.now(timezone.utc)
    session.add(row)
    session.commit()
    session.refresh(row)
    return jsonify(TimeOffRequestPublic.model_validate(row).model_dump())


@router.route("/time-off-requests/<time_off_id>/decline", methods=["PATCH"])
@require_scope("scheduler:admin")
def decline_time_off_request(time_off_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    row = session.get(TimeOffRequest, time_off_id)
    if not row:
        return jsonify({"detail": "Time-off request not found"}), 404
    row.status = TimeOffRequestStatus.declined
    row.updated_on = datetime.now(timezone.utc)
    session.add(row)
    session.commit()
    session.refresh(row)
    return jsonify(TimeOffRequestPublic.model_validate(row).model_dump())


@router.route("/time-off-requests/<time_off_id>", methods=["DELETE"])
@require_scope("member:limited")
def delete_time_off_request(time_off_id: str):
    session = get_db()
    current_user = get_current_user()
    row = session.get(TimeOffRequest, time_off_id)
    if not row:
        return jsonify({"detail": "Time-off request not found"}), 404
    if row.user_id != current_user.id:
        return jsonify({"detail": "Can only delete your own time-off requests"}), 403
    session.delete(row)
    session.commit()
    return jsonify({}), 204


# ── Assignment routes ────


@router.route("/my-assignments", methods=["GET"])
@require_scope("member:limited")
def get_my_assignments():
    session = get_db()
    current_user = get_current_user()
    repo = AssignmentRepository(session=session)
    assignments = repo.get_by_user_id(current_user.id)
    return jsonify(
        AssignmentsPublic(
            data=[AssignmentPublic.model_validate(a) for a in assignments], count=len(assignments)
        ).model_dump()
    )


@router.route("/calendar", methods=["GET"])
@require_scope("member:limited")
def get_calendar_assignments(start_date: str = None, end_date: str = None):
    session = get_db()
    _ = get_current_user()
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    repo = AssignmentRepository(session=session)
    assignments = repo.get_by_date_range(start, end)
    return jsonify(
        AssignmentsPublic(
            data=[AssignmentPublic.model_validate(a) for a in assignments], count=len(assignments)
        ).model_dump()
    )


@router.route("/calendar-with-names", methods=["GET"])
@require_scope("member:limited")
def get_calendar_with_names(start_date: str = None, end_date: str = None):
    session = get_db()
    _ = get_current_user()
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    repo = AssignmentRepository(session=session)
    assignments = repo.get_by_date_range(start, end)
    enriched: list[EnrichedAssignment] = []
    for a in assignments:
        user = session.get(User, a.user_id)
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
    return jsonify(EnrichedAssignmentsResponse(data=enriched, count=len(enriched)).model_dump())


@router.route("/my-calendar", methods=["GET"])
@require_scope("member:limited")
def get_my_calendar(start_date: str = None, end_date: str = None):
    session = get_db()
    current_user = get_current_user()
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    repo = AssignmentRepository(session=session)
    assignments = repo.get_by_user_and_date_range(current_user.id, start, end)
    return jsonify(
        AssignmentsPublic(
            data=[AssignmentPublic.model_validate(a) for a in assignments], count=len(assignments)
        ).model_dump()
    )


@router.route("/", methods=["GET"])
@require_scope("scheduler:admin")
def list_assignments(skip: int = 0, limit: int = 100):
    session = get_db()
    _ = get_current_active_superuser()
    repo = AssignmentRepository(session=session)
    assignments, total_count = repo.get_all(skip=skip, limit=limit)
    return jsonify(
        AssignmentsPublic(
            data=[AssignmentPublic.model_validate(a) for a in assignments], count=total_count
        ).model_dump()
    )


@router.route("/<assignment_id>", methods=["GET"])
@require_scope("scheduler:admin")
def get_assignment(assignment_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    repo = AssignmentRepository(session=session)
    assignment = repo.get_by_id(assignment_id)
    if not assignment:
        return jsonify({"detail": "Assignment not found"}), 404
    return jsonify(AssignmentPublic.model_validate(assignment).model_dump())


@router.route("/", methods=["POST"])
@require_scope("scheduler:admin")
def create_assignment():
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    assignment_in = AssignmentCreate(**data)
    repo = AssignmentRepository(session=session)
    conflicts = repo.check_conflicts(
        user_id=assignment_in.user_id, event_date=assignment_in.event_date
    )
    if conflicts:
        conflict_ids = [c.id for c in conflicts]
        conflict_details = "\n".join(
            f"  - {c.type}: {c.role} on {c.event_date.strftime('%Y-%m-%d')}" for c in conflicts
        )
        return (
            jsonify(
                {
                    "message": "User already has an assignment on this date.",
                    "conflicts": [c.model_dump() for c in conflicts],
                    "conflict_ids": conflict_ids,
                    "details": conflict_details,
                }
            ),
            409,
        )
    assignment = repo.create(assignment_in=assignment_in)
    if assignment is None:
        return jsonify({"detail": "Failed to create assignment"}), 500
    scheduler_svc = SchedulerService(session)
    scheduler_svc.send_assignment_notification(
        user_id=assignment.user_id,
        assignment_type=assignment_in.type.value,
        role=assignment_in.role,
        event_date=assignment.event_date.strftime("%B %d, %Y"),
        instrument=assignment_in.instrument,
        notes=assignment_in.notes,
    )
    return jsonify(AssignmentPublic.model_validate(assignment).model_dump()), 201


@router.route("/<assignment_id>", methods=["PATCH"])
@require_scope("scheduler:admin")
def update_assignment(assignment_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    assignment_in = AssignmentUpdate(**data)
    repo = AssignmentRepository(session=session)
    assignment = repo.get_by_id(assignment_id)
    if not assignment:
        return jsonify({"detail": "Assignment not found"}), 404
    assignment = repo.update(db_assignment=assignment, assignment_in=assignment_in)
    return jsonify(AssignmentPublic.model_validate(assignment).model_dump())


@router.route("/<assignment_id>", methods=["DELETE"])
@require_scope("scheduler:admin")
def delete_assignment(assignment_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    repo = AssignmentRepository(session=session)
    assignment = repo.get_by_id(assignment_id)
    if not assignment:
        return jsonify({"detail": "Assignment not found"}), 404
    repo.delete(db_assignment=assignment)
    return jsonify({}), 204


class BulkAssignResponse(BaseModel):
    created: list[AssignmentPublic]
    conflicts: list[dict[str, Any]]


@router.route("/bulk", methods=["POST"])
@require_scope("scheduler:admin")
def bulk_assign():
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    bulk_in = BulkAssignRequest(**data)
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
        conflicts_check = repo.check_conflicts(user_id=entry.user_id, event_date=bulk_in.event_date)
        if conflicts_check:
            conflicts.append(
                {
                    "user_id": entry.user_id,
                    "message": "User already has an assignment on "
                    + bulk_in.event_date.strftime("%Y-%m-%d"),
                    "conflicts": [c.model_dump() for c in conflicts_check],
                }
            )
            continue
        assignment = repo.create(assignment_in=assignment_in)
        if assignment is None:
            conflicts.append({"user_id": entry.user_id, "message": "Failed to create assignment"})
            continue
        scheduler_svc.send_assignment_notification(
            user_id=assignment.user_id,
            assignment_type=bulk_in.type.value,
            role=entry.role,
            event_date=assignment.event_date.strftime("%B %d, %Y"),
            instrument=entry.instrument,
            notes=entry.notes,
        )
        created.append(AssignmentPublic.model_validate(assignment))
    return jsonify(BulkAssignResponse(created=created, conflicts=conflicts).model_dump()), 201

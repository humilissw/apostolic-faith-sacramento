"""Service for time-off request operations."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TimeOffRequest, TimeOffRequestStatus


class TimeOffRequestService:
    """Handles business logic for time-off requests."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_time_off(
        self,
        user_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[TimeOffRequest]:
        """Get time-off requests for a user with optional date filtering."""
        stmt = select(TimeOffRequest).where(  # type: ignore[arg-type]
            TimeOffRequest.user_id == user_id,  # type: ignore[arg-type]
        )
        if start_date and end_date:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            stmt = stmt.where(TimeOffRequest.date >= start)  # type: ignore[arg-type]
            stmt = stmt.where(TimeOffRequest.date <= end)  # type: ignore[arg-type]
        stmt = stmt.order_by(TimeOffRequest.date)  # type: ignore[arg-type]
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_time_off_request(
        self,
        user_id: str,
        date: datetime,
        notes: str | None = None,
    ) -> TimeOffRequest:
        """Create a new time-off request."""
        row = TimeOffRequest(
            user_id=user_id,
            date=date,
            status=TimeOffRequestStatus.pending,
            notes=notes,
            created_on=datetime.now(timezone.utc),
            updated_on=None,  # type: ignore[assignment]
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def approve_request(self, time_off_id: str) -> TimeOffRequest:
        """Approve a time-off request."""
        row = await self.session.get(TimeOffRequest, time_off_id)  # type: ignore[no-any-return]
        if not row:
            raise ValueError("Time-off request not found")
        row.status = TimeOffRequestStatus.approved
        row.updated_on = datetime.now(timezone.utc)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)  # type: ignore[no-any-return]
        return row

    async def decline_request(self, time_off_id: str) -> TimeOffRequest:
        """Decline a time-off request."""
        row = await self.session.get(TimeOffRequest, time_off_id)  # type: ignore[no-any-return]
        if not row:
            raise ValueError("Time-off request not found")
        row.status = TimeOffRequestStatus.declined
        row.updated_on = datetime.now(timezone.utc)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)  # type: ignore[no-any-return]
        return row

    async def delete_request(self, time_off_id: str, user_id: str) -> None:
        """Delete a time-off request (owner only)."""
        row = await self.session.get(TimeOffRequest, time_off_id)
        if not row:
            raise ValueError("Time-off request not found")
        if row.user_id != user_id:
            raise PermissionError("Can only delete your own time-off requests")
        await self.session.delete(row)
        await self.session.commit()

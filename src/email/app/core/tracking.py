"""Service-owned delivery-tracking database.

Every send request handled by this microservice is recorded here so the
service can account for its own deliveries without touching the shared
application database. Backed by SQLite by default (file under ``data/``);
any SQLAlchemy URL works via the ``TRACKING_DB_URL`` env var.
"""

from __future__ import annotations

import datetime
import uuid
from functools import lru_cache

from sqlalchemy import DateTime, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


class EmailDelivery(Base):
    """One row per delivery attempt (one recipient = one row)."""

    __tablename__ = "email_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # Grouping id: announcements fan out to many recipients under one batch.
    batch_id: Mapped[str] = mapped_column(String(36), index=True)
    email_type: Mapped[str] = mapped_column(String(50), index=True)
    recipient: Mapped[str] = mapped_column(String(320), index=True)
    subject: Mapped[str] = mapped_column(String(500), default="")
    # "sent" | "failed"
    status: Mapped[str] = mapped_column(String(20), index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Identity of the caller (JWT ``sub`` or "api-key"), for auditability.
    requested_by: Mapped[str] = mapped_column(String(320), default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))


@lru_cache(maxsize=1)
def tracking_session_factory() -> sessionmaker[Session]:
    kwargs: dict = {"future": True}
    if ":memory:" in settings.TRACKING_DB_URL:
        # In-memory SQLite: keep one shared connection so every session in the
        # process sees the same database (tests use this).
        from sqlalchemy.pool import StaticPool

        kwargs["poolclass"] = StaticPool
        kwargs["connect_args"] = {"check_same_thread": False}
    elif settings.TRACKING_DB_URL.startswith("sqlite:///"):
        # Ensure a file-backed SQLite tracking DB's parent directory exists.
        from pathlib import Path

        db_path = settings.TRACKING_DB_URL.removeprefix("sqlite:///")
        if db_path and not db_path.startswith(":memory:"):
            Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)
    engine: Engine = create_engine(settings.TRACKING_DB_URL, **kwargs)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_tracking_db() -> None:
    """Create the tracking schema (idempotent). Called on app startup."""
    tracking_session_factory()


def record_delivery(
    *,
    batch_id: str,
    email_type: str,
    recipient: str,
    subject: str,
    status: str,
    error: str | None = None,
    requested_by: str = "",
) -> str:
    """Persist one delivery attempt; returns the tracking row id."""
    session = tracking_session_factory()()
    try:
        row = EmailDelivery(
            id=str(uuid.uuid4()),
            batch_id=batch_id,
            email_type=email_type,
            recipient=recipient,
            subject=subject[:500],
            status=status,
            error=error,
            requested_by=requested_by,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        session.add(row)
        session.commit()
        return row.id
    finally:
        session.close()

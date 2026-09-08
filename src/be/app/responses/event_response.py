from pydantic import BaseModel
from datetime import datetime


class EventPublic(BaseModel):
    id: str
    title: str
    description: str
    date: datetime
    start_time: datetime
    end_time: datetime
    created_on: datetime
    updated_on: datetime | None = None
    # Public URL path for the uploaded flyer image (None when no flyer exists).
    flyer_url: str | None = None


class EventsPublic(BaseModel):
    data: list[EventPublic]
    count: int

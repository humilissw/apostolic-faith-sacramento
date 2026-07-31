from pydantic import BaseModel
from datetime import datetime


class EventPublic(BaseModel):
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    created_on: datetime
    updated_on: datetime | None = None

class EventsPublic(BaseModel):
    data: list[EventPublic]
    count: int

import datetime

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Event creation request schema."""

    event_id: str = Field(max_length=36)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    start_time: datetime.datetime
    end_time: datetime.datetime

class EventUpdate(BaseModel):
    """Event update request schema (all fields optional)."""

    title: str | None = Field(default=None, max_length=200) 
    description: str | None = Field(default=None, max_length=4000)
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
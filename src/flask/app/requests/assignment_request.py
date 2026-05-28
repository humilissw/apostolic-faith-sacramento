import datetime

from pydantic import BaseModel, Field
from app.models import AssignmentType


class AssignmentCreate(BaseModel):
    user_id: str = Field(max_length=36)
    event_date: datetime.datetime
    type: AssignmentType
    role: str = Field(default="", max_length=200)
    instrument: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)
    group_leader: bool = Field(default=False)


class BulkAssignEntry(BaseModel):
    user_id: str = Field(max_length=36)
    role: str = Field(default="", max_length=200)
    instrument: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)
    group_leader: bool = Field(default=False)


class BulkAssignRequest(BaseModel):
    event_date: datetime.datetime
    type: AssignmentType
    entries: list[BulkAssignEntry]


class AssignmentUpdate(BaseModel):
    event_date: datetime.datetime | None = None
    type: AssignmentType | None = None
    role: str | None = Field(default=None, max_length=200)
    instrument: str | None = None
    notes: str | None = None
    group_leader: bool | None = None


class TimeOffRequestCreate(BaseModel):
    date: datetime.datetime
    notes: str | None = Field(default=None, max_length=4000)

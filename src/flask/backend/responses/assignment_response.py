from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AssignmentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    event_date: datetime
    type: str
    role: str
    instrument: str | None
    notes: str | None
    created_on: datetime
    updated_on: datetime | None = None


class AssignmentsPublic(BaseModel):
    data: list[AssignmentPublic]
    count: int

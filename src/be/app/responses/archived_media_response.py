from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ArchivedMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_location: str
    created_on: datetime
    updated_on: datetime | None = None

class ArchivedMediasResponse(BaseModel):
    data: list[ArchivedMediaResponse]
    count: int
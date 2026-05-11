from pydantic import BaseModel
from datetime import datetime


class MediaPublic(BaseModel):
    id: str
    name: str
    uploaded_on: datetime
    created_on: datetime
    updated_on: datetime | None = None


class MediaPublicWithUrl(MediaPublic):
    download_url: str | None = None


class MediasPublic(BaseModel):
    data: list[MediaPublicWithUrl]
    count: int

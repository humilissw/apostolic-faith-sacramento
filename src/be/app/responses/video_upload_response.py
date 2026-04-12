from pydantic import BaseModel
from datetime import datetime


class VideoUploadPublic(BaseModel):
    id: str
    upload_location: str
    upload_name: str
    created_on: datetime
    updated_on: datetime | None = None


class VideoUploadPublicWithUrl(VideoUploadPublic):
    download_url: str | None = None


class VideoUploadsPublic(BaseModel):
    data: list[VideoUploadPublicWithUrl]
    count: int
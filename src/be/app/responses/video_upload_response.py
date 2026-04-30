from pydantic import BaseModel, ConfigDict
from datetime import datetime


class VideoUploadPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    upload_location: str
    upload_name: str
    media_association_date: datetime
    speaker_name: str | None
    reference_text: str | None
    description: str | None
    created_on: datetime
    updated_on: datetime | None = None


class VideoUploadPublicWithUrl(VideoUploadPublic):
    download_url: str | None = None


class VideoUploadsPublic(BaseModel):
    data: list[VideoUploadPublicWithUrl]
    count: int

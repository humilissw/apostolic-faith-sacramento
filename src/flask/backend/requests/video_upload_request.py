import datetime

from pydantic import BaseModel, Field


class VideoUploadCreate(BaseModel):
    upload_location: str = Field(..., max_length=1000)
    upload_name: str = Field(..., max_length=1000)
    media_association_date: datetime.datetime = Field()
    speaker_name: str | None = Field(default=None, max_length=200)
    reference_text: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=4000)


class VideoUploadUpdate(BaseModel):
    upload_location: str | None = Field(default=None, max_length=1000)
    upload_name: str | None = Field(default=None, max_length=1000)
    media_association_date: datetime.datetime | None = Field(default=None)
    speaker_name: str | None = Field(default=None, max_length=200)
    reference_text: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=4000)

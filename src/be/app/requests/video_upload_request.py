from pydantic import BaseModel, Field


class VideoUploadCreate(BaseModel):
    upload_location: str = Field(..., max_length=1000)
    upload_name: str = Field(..., max_length=1000)


class VideoUploadUpdate(BaseModel):
    upload_location: str | None = Field(default=None, max_length=1000)
    upload_name: str | None = Field(default=None, max_length=1000)
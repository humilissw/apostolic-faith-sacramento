from pydantic import BaseModel, Field


class MediaCreate(BaseModel):
    name: str = Field(..., min_length=0, max_length=200)


class MediaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)

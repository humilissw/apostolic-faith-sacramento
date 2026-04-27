from pydantic import BaseModel


class VideoRequest(BaseModel):
    upload_name: str
    upload_location: str

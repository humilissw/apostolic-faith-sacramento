from datetime import date

from pydantic import BaseModel


class VideoRequest(BaseModel):
    upload_name: str
    upload_location: str
    media_association_date: date
    speaker_name: str
    reference_text: str
    description: str

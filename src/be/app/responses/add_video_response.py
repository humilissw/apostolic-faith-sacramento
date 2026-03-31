from pydantic import BaseModel
from sqlmodel import Session
from app.requests.church_service_request import ChurchServiceRequest


class AddVideoResponse(BaseModel):
    video_name: str

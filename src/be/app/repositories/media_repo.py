from app.models import Media
from app.requests.video_request import VideoRequest
from sqlmodel import Session, select
from app.requests.church_service_request import ChurchServiceRequest


class MediaRepo:

    def __init__(self, session: Session):
        self.session = session
        

    async def get_services(self, skip: int | None, takeAmt: int | None):
        mediaItems = await self.session.exec(
            select(Media).limit(takeAmt).offset(skip)
        ).fetchmany(100)
        return mediaItems

    async def update_services(self) -> int:
        mediaItems = await self.session.exec(
            select(Media).limit(takeAmt).offset(skip)
        ).fetchmany(100)

    def delete_service(self):
        pass

    def add_new_video(self, video: VideoRequest):
        
        pass

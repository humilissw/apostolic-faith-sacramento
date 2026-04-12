from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models import Media, VideoUpload, VideoUploadRequest
from app.requests.video_request import VideoRequest
from sqlmodel import Session
from app.requests.church_service_request import ChurchServiceRequest
from app.responses.add_video_response import AddVideoResponse
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class MediaService:

    def __init__(self):
        pass

    def get_media(self):
        pass

    def update_services(self):
        pass

    def delete_service(self):
        pass

    async def add_new_video(
        self, session: AsyncSession, video: VideoRequest
    ) -> AddVideoResponse:
        is_valid = VideoRequest.model_validate(video)

        session.add(VideoUpload(upload_name=video.upload_name, upload_location=video.upload_location))
        await session.commit()

        statement = select(VideoUpload).where(
            VideoUpload.upload_name == video.upload_name,
            VideoUpload.upload_location == video.upload_location
        )
        video_result = await session.execute(statement)
        new_video = video_result.scalar()

        return AddVideoResponse(upload_name=new_video.upload_name, id=new_video.id)

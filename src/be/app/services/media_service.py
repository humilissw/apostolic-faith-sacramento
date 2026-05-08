from sqlalchemy import select

from fastapi import HTTPException

from app.models import VideoUpload
from app.requests.video_request import VideoRequest
from app.responses.add_video_response import AddVideoResponse
from sqlalchemy.ext.asyncio import AsyncSession


class MediaService:
    def __init__(self):
        pass

    def get_media(self):
        pass

    def update_services(self):
        pass

    def delete_service(self):
        pass

    async def add_new_video(self, session: AsyncSession, video: VideoRequest) -> AddVideoResponse:
        session.add(
            VideoUpload(upload_name=video.upload_name, upload_location=video.upload_location)
        )
        await session.commit()

        statement = select(VideoUpload).where(  # type: ignore[arg-type]
            VideoUpload.upload_name == video.upload_name,  # type: ignore[arg-type]
            VideoUpload.upload_location == video.upload_location,  # type: ignore[arg-type]
        )
        video_result = await session.execute(statement)
        new_video = video_result.scalar()

        if new_video is None:
            raise HTTPException(status_code=404, detail="Video upload not found")

        return AddVideoResponse(upload_name=new_video.upload_name, id=new_video.id)

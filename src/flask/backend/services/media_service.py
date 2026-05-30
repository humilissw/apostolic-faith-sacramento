from sqlalchemy import select

from werkzeug.exceptions import HTTPException
from backend.models import VideoUpload
from backend.requests.video_request import VideoRequest
from backend.responses.add_video_response import AddVideoResponse


class MediaService:
    def __init__(self):
        pass

    def get_media(self):
        pass

    def update_services(self):
        pass

    def delete_service(self):
        pass

    def add_new_video(self, session, video: VideoRequest) -> AddVideoResponse:
        session.add(VideoUpload(upload_name=video.upload_name, upload_location=video.upload_location))
        session.commit()

        statement = select(VideoUpload).where(
            VideoUpload.upload_name == video.upload_name,
            VideoUpload.upload_location == video.upload_location,
        )
        video_result = session.execute(statement)
        new_video = video_result.scalar()

        if new_video is None:
            raise HTTPException(404, detail="Video upload not found")

        return AddVideoResponse(upload_name=new_video.upload_name, id=new_video.id)

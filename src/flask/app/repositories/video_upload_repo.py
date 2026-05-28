from sqlalchemy import select, func
from app.models import VideoUpload
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate
from datetime import datetime, timezone


class VideoUploadRepository:
    def __init__(self, session):
        self.session = session

    def create(self, video_upload_in: VideoUploadCreate, owner_id: str) -> VideoUpload:
        video_upload = VideoUpload(
            owner_id=owner_id,
            upload_location=video_upload_in.upload_location,
            upload_name=video_upload_in.upload_name,
            description=video_upload_in.description,
            media_association_date=video_upload_in.media_association_date,
            speaker_name=video_upload_in.speaker_name,
            reference_text=video_upload_in.reference_text,
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )
        self.session.add(video_upload)
        self.session.commit()
        self.session.refresh(video_upload)
        return video_upload

    def get_by_id(self, video_upload_id: str) -> VideoUpload | None:
        statement = select(VideoUpload).where(VideoUpload.id == video_upload_id)
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[VideoUpload], int]:
        count_statement = select(func.count()).select_from(VideoUpload)
        count_result = self.session.execute(count_statement)
        total_count = count_result.scalar()
        statement = select(VideoUpload).offset(skip).limit(limit)
        result = self.session.execute(statement)
        video_uploads = result.scalars().all()
        return list(video_uploads), total_count or 0

    def update(
        self, db_video_upload: VideoUpload, video_upload_in: VideoUploadUpdate
    ) -> VideoUpload:
        update_data = video_upload_in.model_dump(exclude_unset=True)
        update_data["updated_on"] = datetime.now(timezone.utc)
        if "created_on" in update_data:
            del update_data["created_on"]
        db_video_upload.sqlmodel_update(update_data)
        self.session.add(db_video_upload)
        self.session.commit()
        self.session.refresh(db_video_upload)
        return db_video_upload

    def delete(self, db_video_upload: VideoUpload) -> None:
        self.session.delete(db_video_upload)
        self.session.commit()

"""Service for video upload management operations."""

from app.models import Message
from app.repositories.video_upload_repo import VideoUploadRepository
from app.responses.video_upload_response import (
    VideoUploadPublic,
    VideoUploadPublicWithUrl,
)


class VideoUploadManagementService:
    """Handles business logic for video upload management operations."""

    def __init__(self, session):
        self.session = session

    async def get_all_video_uploads(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        """Get all video uploads with pagination."""
        repository = VideoUploadRepository(session=self.session)
        video_uploads, total_count = await repository.get_all(skip=skip, limit=limit)

        # Add download URLs (placeholder - should be implemented based on storage)
        video_upload_data = [
            VideoUploadPublicWithUrl(
                id=v.id,
                upload_location=v.upload_location,
                upload_name=v.upload_name,
                description=v.description,
                reference_text=v.reference_text,
                speaker_name=v.speaker_name,
                media_association_date=v.media_association_date,
                created_on=v.created_on,
                updated_on=v.updated_on,
                download_url=v.upload_location,
            )
            for v in video_uploads
        ]

        return video_upload_data, total_count

    async def get_video_upload_by_id(self, video_upload_id: str) -> VideoUploadPublic | None:
        """Get video upload by ID."""
        repository = VideoUploadRepository(session=self.session)
        video_upload = await repository.get_by_id(video_upload_id=video_upload_id)
        if not video_upload:
            return None

        return VideoUploadPublic(
            id=video_upload.id,
            upload_location=video_upload.upload_location,
            upload_name=video_upload.upload_name,
            description=video_upload.description,
            reference_text=video_upload.reference_text,
            speaker_name=video_upload.speaker_name,
            media_association_date=video_upload.media_association_date,
            created_on=video_upload.created_on,
            updated_on=video_upload.updated_on,
        )

    async def update_video_upload(
        self, video_upload_id: str, current_user, video_upload_in
    ) -> VideoUploadPublic | None:
        """Update a video upload entry (requires ownership or superuser)."""
        repository = VideoUploadRepository(session=self.session)
        video_upload = await repository.get_by_id(video_upload_id=video_upload_id)
        if not video_upload:
            return None
        if current_user.id != video_upload.owner_id and not current_user.is_superuser:
            raise PermissionError("Not authorized to update this video upload")

        video_upload = await repository.update(
            db_video_upload=video_upload, video_upload_in=video_upload_in
        )
        return VideoUploadPublic(
            id=video_upload.id,
            upload_location=video_upload.upload_location,
            description=video_upload.description,
            reference_text=video_upload.reference_text,
            speaker_name=video_upload.speaker_name,
            media_association_date=video_upload.media_association_date,
            upload_name=video_upload.upload_name,
            created_on=video_upload.created_on,
            updated_on=video_upload.updated_on,
        )

    async def delete_video_upload(self, video_upload_id: str, current_user) -> Message | None:
        """Delete a video upload entry (requires ownership or superuser)."""
        repository = VideoUploadRepository(session=self.session)
        video_upload = await repository.get_by_id(video_upload_id=video_upload_id)
        if not video_upload:
            return None
        if current_user.id != video_upload.owner_id and not current_user.is_superuser:
            raise PermissionError("Not authorized to delete this video upload")

        await repository.delete(db_video_upload=video_upload)
        return Message(message="Video upload deleted successfully")

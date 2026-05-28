from sqlalchemy import select, func
from werkzeug.exceptions import HTTPException
from app.models import Media
from app.requests.media_request import MediaCreate, MediaUpdate
from datetime import datetime, timezone


class MediaRepository:
    def __init__(self, session):
        self.session = session

    def create(self, media_in: MediaCreate, owner_id: str) -> Media:
        try:
            media = Media(
                name=media_in.name,
                owner_id=owner_id,
                uploaded_on=datetime.now(timezone.utc),
                created_on=datetime.now(timezone.utc),
                updated_on=datetime.now(timezone.utc),
            )
            self.session.add(media)
            self.session.commit()
            self.session.refresh(media)
            return media
        except Exception:
            raise HTTPException(500, "Database error occurred while creating media")

    def get_by_id(self, media_id: str) -> Media | None:
        try:
            statement = select(Media).where(Media.id == media_id)
            result = self.session.execute(statement)
            return result.scalar_one_or_none()
        except Exception:
            raise HTTPException(500, "Database error occurred while retrieving media")

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Media], int]:
        try:
            count_statement = select(func.count()).select_from(Media)
            count_result = self.session.execute(count_statement)
            total_count = count_result.scalar()
        except Exception:
            raise HTTPException(500, "Database error occurred while counting media")
        try:
            statement = select(Media).offset(skip).limit(limit)
            result = self.session.execute(statement)
            medias = result.scalars().all()
        except Exception:
            raise HTTPException(500, "Database error occurred while retrieving media list")
        return list(medias), total_count or 0

    def update(self, db_media: Media, media_in: MediaUpdate) -> Media:
        if db_media is None:
            raise HTTPException(404, detail="Media not found")
        update_data = media_in.model_dump(exclude_unset=True)
        update_data["updated_on"] = datetime.now(timezone.utc)
        if "created_on" in update_data:
            del update_data["created_on"]
        db_media.sqlmodel_update(update_data)
        self.session.add(db_media)
        self.session.commit()
        self.session.refresh(db_media)
        return db_media

    def delete(self, db_media: Media) -> None:
        if db_media is None:
            return
        self.session.delete(db_media)
        self.session.commit()

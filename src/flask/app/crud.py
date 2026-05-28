import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, Media, User, UserCreate, UserUpdate, VideoUpload
from app.requests.media_request import MediaCreate, MediaUpdate
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate


def create_user(*, session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    from app.models import UserScope

    session.add(UserScope(user_id=db_obj.id, scope="member:limited"))
    session.commit()
    if user_create.is_superuser:
        session.add(UserScope(user_id=db_obj.id, scope="superuser"))
        session.commit()
    return db_obj


def update_user(*, session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.execute(statement)
    return session_user.scalar()


def authenticate(*, session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_media(*, session, media_in: MediaCreate, owner_id: str) -> Media:
    media = Media(
        name=media_in.name,
        owner_id=owner_id,
        uploaded_on=datetime.now(timezone.utc),
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc),
    )
    session.add(media)
    session.commit()
    session.refresh(media)
    return media


def get_media_by_id(*, session, media_id: str) -> Media | None:
    statement = select(Media).where(Media.id == media_id)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def get_media(*, session, skip: int = 0, limit: int = 100) -> list[Media]:
    statement = select(Media).offset(skip).limit(limit)
    result = session.execute(statement)
    return list(result.scalars().all())


def update_media(*, session, db_media: Media, media_in: MediaUpdate) -> Media:
    update_data = media_in.model_dump(exclude_unset=True)
    update_data["updated_on"] = datetime.now(timezone.utc)
    if "created_on" in update_data:
        del update_data["created_on"]
    db_media.sqlmodel_update(update_data)
    session.add(db_media)
    session.commit()
    session.refresh(db_media)
    return db_media


def delete_media(*, session, db_media: Media) -> None:
    session.delete(db_media)
    session.commit()


def create_video_upload(
    *, session, video_upload_in: VideoUploadCreate, owner_id: str
) -> VideoUpload:
    video_upload = VideoUpload(
        owner_id=owner_id,
        upload_location=video_upload_in.upload_location,
        upload_name=video_upload_in.upload_name,
        media_association_date=datetime.now(timezone.utc),
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc),
    )
    session.add(video_upload)
    session.commit()
    session.refresh(video_upload)
    return video_upload


def get_video_upload_by_id(*, session, video_upload_id: str) -> VideoUpload | None:
    statement = select(VideoUpload).where(VideoUpload.id == video_upload_id)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def get_video_upload(*, session, skip: int = 0, limit: int = 100) -> list[VideoUpload]:
    statement = select(VideoUpload).offset(skip).limit(limit)
    result = session.execute(statement)
    return list(result.scalars().all())


def update_video_upload(
    *, session, db_video_upload: VideoUpload, video_upload_in: VideoUploadUpdate
) -> VideoUpload:
    update_data = video_upload_in.model_dump(exclude_unset=True)
    update_data["updated_on"] = datetime.now(timezone.utc)
    if "created_on" in update_data:
        del update_data["created_on"]
    db_video_upload.sqlmodel_update(update_data)
    session.add(db_video_upload)
    session.commit()
    session.refresh(db_video_upload)
    return db_video_upload


def delete_video_upload(*, session, db_video_upload: VideoUpload) -> None:
    session.delete(db_video_upload)
    session.commit()

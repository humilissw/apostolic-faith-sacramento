import secrets
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    Media,
    User,
    UserCreate,
    UserUpdate,
    VideoUpload,
)
from app.requests.media_request import MediaCreate, MediaUpdate
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    # Admin-created users never supply a password; they get a random unusable
    # hash and set their own password via the signed one-time email link.
    password = (
        user_create.password if user_create.password is not None else secrets.token_urlsafe(32)
    )
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    from app.models import UserScope

    # Seed member:limited scope for all users
    session.add(UserScope(user_id=db_obj.id, scope="member:limited"))
    await session.commit()
    # Seed superuser scope if requested
    if user_create.is_superuser:
        session.add(UserScope(user_id=db_obj.id, scope="superuser"))
        await session.commit()
    return db_obj  # type: ignore[no-any-return]


async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> Any:
    # NOTE: password is intentionally not updatable here (UserUpdate has no
    # password field). Passwords are only changed by the user themselves via
    # /users/me/password or a signed one-time email link.
    user_data = user_in.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user_password(*, session: AsyncSession, db_user: User, new_password: str) -> User:
    """Set a user's password (used by self-service and email-link flows only)."""
    db_user.hashed_password = get_password_hash(new_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)  # type: ignore[arg-type]
    session_user = await session.execute(statement)
    return session_user.scalar()  # type: ignore[no-any-return]


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


async def create_item(*, session: AsyncSession, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item  # type: ignore[no-any-return]


# Media CRUD operations
async def create_media(*, session: AsyncSession, media_in: MediaCreate, owner_id: str) -> Media:
    """Create a new media entry."""
    media = Media(
        name=media_in.name,
        owner_id=owner_id,
        uploaded_on=datetime.now(UTC),
        created_on=datetime.now(UTC),
        updated_on=datetime.now(UTC),
    )
    session.add(media)
    await session.commit()
    await session.refresh(media)
    return media


async def get_media_by_id(*, session: AsyncSession, media_id: str) -> Media | None:
    """Get media by ID."""
    statement = select(Media).where(Media.id == media_id)  # type: ignore[arg-type]
    result = await session.execute(statement)
    return result.scalar_one_or_none()  # type: ignore[no-any-return]


async def get_media(*, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Media]:
    """Get all media entries with pagination."""
    statement = select(Media).offset(skip).limit(limit)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def update_media(*, session: AsyncSession, db_media: Media, media_in: MediaUpdate) -> Media:
    """Update a media entry."""
    update_data = media_in.model_dump(exclude_unset=True)
    update_data["updated_on"] = datetime.now(UTC)

    # Handle datetime fields
    if "created_on" in update_data:
        del update_data["created_on"]

    db_media.sqlmodel_update(update_data)
    session.add(db_media)
    await session.commit()
    await session.refresh(db_media)
    return db_media


async def delete_media(*, session: AsyncSession, db_media: Media) -> None:
    """Delete a media entry."""
    await session.delete(db_media)
    await session.commit()


# Video Upload CRUD operations
async def create_video_upload(
    *, session: AsyncSession, video_upload_in: VideoUploadCreate, owner_id: str
) -> VideoUpload:
    """Create a new video upload entry."""
    video_upload = VideoUpload(
        owner_id=owner_id,
        upload_location=video_upload_in.upload_location,
        upload_name=video_upload_in.upload_name,
        media_association_date=datetime.now(UTC),
        created_on=datetime.now(UTC),
        updated_on=datetime.now(UTC),
    )
    session.add(video_upload)
    await session.commit()
    await session.refresh(video_upload)
    return video_upload


async def get_video_upload_by_id(
    *, session: AsyncSession, video_upload_id: str
) -> VideoUpload | None:
    """Get video upload by ID."""
    statement = select(VideoUpload).where(
        VideoUpload.id == video_upload_id  # type: ignore[arg-type]
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()  # type: ignore[no-any-return]


async def get_video_upload(
    *, session: AsyncSession, skip: int = 0, limit: int = 100
) -> list[VideoUpload]:
    """Get all video uploads with pagination."""
    statement = select(VideoUpload).offset(skip).limit(limit)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def update_video_upload(
    *,
    session: AsyncSession,
    db_video_upload: VideoUpload,
    video_upload_in: VideoUploadUpdate,
) -> VideoUpload:
    """Update a video upload entry."""
    update_data = video_upload_in.model_dump(exclude_unset=True)
    update_data["updated_on"] = datetime.now(UTC)

    # Handle datetime fields
    if "created_on" in update_data:
        del update_data["created_on"]

    db_video_upload.sqlmodel_update(update_data)
    session.add(db_video_upload)
    await session.commit()
    await session.refresh(db_video_upload)
    return db_video_upload


async def delete_video_upload(*, session: AsyncSession, db_video_upload: VideoUpload) -> None:
    """Delete a video upload entry."""
    await session.delete(db_video_upload)
    await session.commit()

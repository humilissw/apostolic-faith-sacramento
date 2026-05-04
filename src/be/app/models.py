import datetime
from typing import Annotated, Optional
import uuid

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel

# notes for future self:
# pydantic expects the model tree to be as follows when working with objects.
#  Root model -> SQLModel
#     Build a type with this model if you want to return a subset of properties
#     from a given SQL model.
#     Example: Model has field A, B, C, but I only want to return A.
#     Create a subclass from the class with the SQLModel-subclass.
#     (see UserBase as an example and UserPublic as an example)
# Then you can subclass stuff as expected.
# Don't forget that the type has to have overlapping properties from a store,
# so if you are trying to return a type that doesn't have stuff in the store, it won't work.
# You need to make sure that the subclass somehow maps back to the base class with the SQLModel type


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), max_length=36, primary_key=True)
    hashed_password: str = Field(max_length=4000)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_on: datetime.datetime | None = Field(nullable=True, default=None)
    new_id: str = Field(default_factory=lambda: str(uuid.uuid4()), max_length=36, exclude=True)
    # items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(SQLModel):
    email: EmailStr
    is_active: bool
    is_superuser: bool
    new_id: str
    full_name: Annotated[str | None, Field(exclude=True)]


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "items"
    id: int | None = Field(primary_key=True, default=None)
    owner_id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=36, nullable=False
    )
    created_on: datetime.datetime | None = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_on: datetime.datetime | None = Field(nullable=True, default=None)
    # owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: str


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


class HealthPublic:
    is_healthy: bool


# Generic message
class Message(SQLModel):
    message: str = Field(default=None, min_length=8, max_length=4000)


# JSON payload containing access token
class Token(SQLModel):
    access_token: str = Field(default=None, min_length=8, max_length=4000)
    refresh_token: str = Field(default=None, min_length=8, max_length=4000)
    token_type: str = "bearer"
    access_token_expires: int = Field(default=0)
    refresh_token_expires: int = Field(default=0)
    scopes: list[str] = Field(default_factory=list)


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
    iss: str | None = None
    aud: str | None = None
    jti: str | None = None
    scopes: list[str] | None = None


class NewPassword(SQLModel):
    token: str = Field(max_length=4000)
    new_password: str = Field(min_length=8, max_length=128)


# Refresh token storage model
class RefreshToken(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "refresh_tokens"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    user_id: str = Field(nullable=False)
    token: str = Field(max_length=4000, nullable=False, unique=True)
    revoked: bool = Field(default=False)
    expires_at: datetime.datetime = Field(nullable=False)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )


class UpdateTokenResponse(SQLModel):
    access_token: str = Field(min_length=8, max_length=4000)
    token_type: str = "bearer"
    access_token_expires: int = Field(default=0)
    scopes: list[str] = Field(default_factory=list)


class TokenRefresh(SQLModel):
    refresh_token: str = Field(min_length=8, max_length=4000)


class RevokeTokenRequest(SQLModel):
    token: str = Field(min_length=8, max_length=4000)


class Media(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "media"
    id: str = Field(default_factory=uuid.uuid4, primary_key=True, max_length=36)
    name: str = Field(max_length=200)
    owner_id: str = Field(max_length=36, nullable=False)
    uploaded_on: datetime.datetime
    created_on: datetime.datetime
    updated_on: datetime.datetime


class Test(SQLModel, table=True):  # type: ignore[call-arg]
    id: str = Field(default_factory=uuid.uuid4, primary_key=True, max_length=36)
    test1: int
    test2: int
    test3: int
    test4: int


class DefaultBase(SQLModel):
    id: str = Field(default_factory=uuid.uuid4, primary_key=True, max_length=36)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_on: datetime.datetime = Field(nullable=True)


class Member(DefaultBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "members"
    first_name: str = Field(max_length=200, nullable=False)
    last_name: str = Field(max_length=200, nullable=False)
    birthday: datetime.datetime = Field(nullable=False)
    wedding_anniversary: datetime.datetime = Field(nullable=True)
    baptism_date: datetime.datetime


class ChurchService(DefaultBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "church_services"
    service_date: datetime.datetime = Field(nullable=False)
    speaker: str = Field(max_length=200, nullable=True)
    service_title: Optional[str] = Field(max_length=200, nullable=True)
    file_location: Optional[str] = Field(max_length=1000, nullable=True)
    edited: bool = Field(nullable=False, default=False)
    uploaded: bool = Field(nullable=False, default=False)


class VideoUpload(DefaultBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "video_uploads"
    owner_id: str = Field(max_length=36, nullable=False)
    upload_location: str = Field(max_length=1000)
    upload_name: str = Field(max_length=1000)
    media_association_date: datetime.datetime = Field(nullable=False)
    speaker_name: str = Field(max_length=200, nullable=True)
    reference_text: str = Field(max_length=50, nullable=True)
    description: str = Field(max_length=4000, nullable=True)


class VideoUploadBase(SQLModel):
    id: Annotated[str, Field(exclude=True)]
    created_on: Annotated[datetime.datetime, Field(exclude=True)]
    updated_on: Annotated[datetime.datetime, Field(exclude=True)]
    upload_location: Annotated[str, Field(exclude=True)]


class VideoUploadRequest(BaseModel):
    upload_name: str


class Announcement(DefaultBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "announcements"
    sender: str = Field(max_length=200)
    recipients: str = Field(max_length=4000)
    message: str = Field(max_length=4000)


# Payment / Donation models


class Payment(DefaultBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "payments"
    amount_cents: int = Field(nullable=False)
    currency: str = Field(default="usd", max_length=3)
    status: str = Field(default="pending", max_length=20)  # pending, succeeded, failed, refunded
    stripe_payment_intent_id: str = Field(max_length=255, nullable=False, unique=True)
    stripe_subscription_id: str | None = Field(default=None, max_length=255)
    donor_email: str | None = Field(default=None, max_length=255)
    donor_name: str | None = Field(default=None, max_length=255)
    receipt_url: str | None = Field(default=None, max_length=1000)
    metadata_json: str | None = Field(default=None, max_length=4000)


class DonationConfig(DefaultBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "donation_configs"
    label: str = Field(max_length=100)
    amount_cents: int = Field(nullable=False)
    is_default: bool = Field(default=False)
    frequency: str = Field(max_length=20)  # one_time or recurring


# Third-party integration configuration models


class IntegrationConfigBase(SQLModel):
    """Shared properties for integration configs."""

    type: str = Field(max_length=50)
    display_name: str = Field(max_length=100)
    icon: str = Field(default="Plug", max_length=50)
    enabled: bool = False
    status: str = Field(default="disconnected", max_length=20)


class IntegrationConfigCreate(IntegrationConfigBase):
    """Properties to receive via API on creation."""

    config_json: str | None = Field(default=None, max_length=4000)
    credentials: dict[str, str] = Field(default_factory=dict)


class IntegrationConfigUpdate(SQLModel):
    """Properties to receive via API on update (all optional)."""

    display_name: str | None = Field(default=None, max_length=100)
    icon: str | None = Field(default=None, max_length=50)
    enabled: bool | None = None
    status: str | None = Field(default=None, max_length=20)
    config_json: str | None = Field(default=None, max_length=4000)


class IntegrationConfigPublic(IntegrationConfigBase):
    """Properties to return via API (credentials stripped)."""

    id: str
    created_on: datetime.datetime
    updated_on: datetime.datetime | None
    config_json: str | None = Field(default=None, max_length=4000)


class IntegrationConfigPublicWithCreds(IntegrationConfigPublic):
    """Integration config with masked credential fields."""

    credential_fields: dict[str, str] = Field(default_factory=dict)


class IntegrationsPublic(SQLModel):
    """Paginated list of integration configs."""

    data: list[IntegrationConfigPublic]
    count: int


class TestConnectionResponse(SQLModel):
    """Response from testing a third-party connection."""

    success: bool
    status: str
    message: str = ""


class IntegrationConfig(DefaultBase, table=True):  # type: ignore[call-arg]
    """Third-party integration configuration with encrypted credentials."""

    __tablename__ = "integration_configs"
    type: str = Field(max_length=50, unique=True)
    display_name: str = Field(max_length=100)
    icon: str = Field(default="Plug", max_length=50)
    enabled: bool = Field(default=False)
    status: str = Field(default="disconnected", max_length=20)
    last_synced_at: datetime.datetime | None = Field(default=None, nullable=True)
    config_json: str | None = Field(default=None, max_length=4000)
    cred_key_id: str | None = Field(default=None, max_length=100)
    cred_encrypted_iv: str | None = Field(default=None, max_length=255)
    cred_encrypted_blob: str | None = Field(default=None, max_length=4000)

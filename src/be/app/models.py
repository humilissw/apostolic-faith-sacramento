import datetime
from enum import Enum
from typing import Annotated, Optional
import uuid

from pydantic import BaseModel, EmailStr
from sqlalchemy import Index as saIndex
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
    scopes: list[str] = Field(default_factory=list)


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
class UserScope(SQLModel, table=True):  # type: ignore[call-arg]
    """Maps users to their assigned scopes (claims)."""

    __tablename__ = "user_scopes"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    user_id: str = Field(foreign_key="users.id", max_length=36, nullable=False)
    scope: str = Field(max_length=50, nullable=False)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )


class UserPublic(SQLModel):
    email: EmailStr
    is_active: bool
    id: str = Field(max_length=36)
    new_id: str
    full_name: Annotated[str | None, Field(exclude=True)]
    assigned_scopes: list[str] = Field(default_factory=list)


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
    refresh_token: str | None = Field(default=None, max_length=4000)
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


class TokenScopes(SQLModel):
    """Decoded token scopes and associated user info."""

    email: str
    scopes: list[str]
    sub: str | None = None
    iss: str | None = None
    aud: str | None = None
    jti: str | None = None


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


# OAuth2 client credentials model


class AuthorizationCode(SQLModel, table=True):  # type: ignore[call-arg]
    """Stores authorization codes for the authorization code flow with PKCE."""

    __tablename__ = "authorization_codes"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    code: str = Field(max_length=200, unique=True)
    client_id: str = Field(max_length=100)
    code_challenge: str = Field(max_length=200)
    redirect_uri: str = Field(default="", max_length=1000)
    used: bool = Field(default=False)
    expires_at: datetime.datetime = Field(nullable=False)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )


class ClientCredentials(SQLModel, table=True):  # type: ignore[call-arg]
    """OAuth2 client credentials for service-to-service auth."""

    __tablename__ = "client_credentials"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    client_id: str = Field(max_length=100, unique=True)
    client_secret_hash: str = Field(max_length=4000)
    scopes: str = Field(max_length=1000)  # comma-separated scope values
    is_active: bool = Field(default=True)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )


class ClientCredentialsPublic(SQLModel):
    id: str
    client_id: str
    scopes: list[str]
    is_active: bool


class ClientCredentialsCreate(SQLModel):
    client_id: str
    scopes: list[str]


class ClientCredentialsUpdate(SQLModel):
    scopes: list[str] | None = None
    is_active: bool | None = None


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
    updated_on: datetime.datetime | None = Field(  # type: ignore
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=True,
    )


# Scheduler models


class AssignmentType(str, Enum):
    music = "music"
    service = "service"


class Assignment(DefaultBase, table=True):  # type: ignore[call-arg]
    """Assignment of a user to a church service or music event."""

    __tablename__ = "assignments"
    user_id: str = Field(max_length=36, nullable=False)
    event_date: datetime.datetime = Field(nullable=False)
    type: AssignmentType = Field(max_length=10, nullable=False)
    role: str = Field(default="", max_length=200, nullable=False)
    instrument: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)
    group_leader: bool = Field(default=False)
    __table_args__ = (
        saIndex("ix_assignments_user_id", "user_id"),
        saIndex("ix_assignments_event_date", "event_date"),
    )


class AssignmentPublic(BaseModel):
    """Assignment response schema."""

    model_config = {"from_attributes": True}
    id: str
    user_id: str
    event_date: datetime.datetime
    type: str
    role: str
    instrument: str | None
    notes: str | None
    group_leader: bool
    created_on: datetime.datetime
    updated_on: datetime.datetime | None


class AssignmentCreate(BaseModel):
    """Assignment creation request schema."""

    user_id: str = Field(max_length=36)
    event_date: datetime.datetime
    type: AssignmentType
    role: str = Field(default="", max_length=200)
    instrument: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)


class AssignmentUpdate(BaseModel):
    """Assignment update request schema (all fields optional)."""

    event_date: datetime.datetime | None = None
    type: AssignmentType | None = None
    role: str | None = Field(default=None, max_length=200)
    instrument: str | None = None
    notes: str | None = None


class TimeOffRequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"


class TimeOffRequest(DefaultBase, table=True):  # type: ignore[call-arg]
    """Time-off request submitted by a user."""

    __tablename__ = "time_off_requests"
    user_id: str = Field(max_length=36, nullable=False)
    date: datetime.datetime = Field(nullable=False)
    status: TimeOffRequestStatus = Field(default=TimeOffRequestStatus.pending, max_length=20)
    notes: str | None = Field(default=None, max_length=4000)


class TimeOffRequestPublic(BaseModel):
    """Time-off request response schema."""

    model_config = {"from_attributes": True}
    id: str
    user_id: str
    date: datetime.datetime
    status: str
    notes: str | None
    created_on: datetime.datetime
    updated_on: datetime.datetime | None


class TimeOffRequestCreate(BaseModel):
    """Time-off request creation schema."""

    date: datetime.datetime
    notes: str | None = Field(default=None, max_length=4000)


class AssignmentsPublic(BaseModel):
    """Paginated assignments response schema."""

    data: list[AssignmentPublic]
    count: int


# Feature flag models


class FeatureFlagBase(SQLModel):
    """Base properties for feature flags."""

    name: str = Field(max_length=100, unique=True)
    description: str = Field(max_length=500)
    is_enabled: bool = Field(default=True)


class FeatureFlagCreate(FeatureFlagBase):
    """Properties to receive via API on creation."""

    pass


class FeatureFlagUpdate(SQLModel):
    """Properties to receive via API on update (all optional)."""

    is_enabled: bool | None = None
    description: str | None = None


class FeatureFlag(FeatureFlagBase, table=True):  # type: ignore[call-arg]
    """Feature flag for controlling feature visibility."""

    __tablename__ = "feature_flags"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_on: datetime.datetime | None = Field(default=None, nullable=True)


class FeatureFlagPublic(FeatureFlagBase):
    """Properties to return via API (id, timestamps)."""

    id: str
    created_on: datetime.datetime
    updated_on: datetime.datetime | None


class FeatureFlagsPublic(SQLModel):
    """Paginated list of feature flags."""

    data: list[FeatureFlagPublic]
    count: int

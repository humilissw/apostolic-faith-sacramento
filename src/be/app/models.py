import datetime
from typing import Annotated, Optional
import uuid

from pydantic import BaseModel, EmailStr
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

# notes for future self:
# pydantic expects the model tree to be as follows when working with objects.
#  Root model -> SQLModel
#     Build a type with this model if you want to return a subset of properties from a given SQL model.  
#     Example: Model has field A, B, C, but I only want to return A.  Create a subclass from the class with the SQLModel-sublcass
#     (see UserBase as an example and UserPublic as an example)
# Then you can subclass stuff as expected.  
# Don't forget that the type has to have overlapping properties from a store, so if you are trying to return a type 
# that doesn't have stuff that is in the store, it won't work as expected.
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
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    new_id: str = Field(default_factory=uuid.uuid4, max_length=36)
    hashed_password: str = Field(max_length=4000)
    created_on: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_on: datetime.datetime | None = Field(nullable=True, default=None)
    # items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(SQLModel):
    email: EmailStr
    is_active: bool
    is_superuser: bool
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
class Item(ItemBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    owner_id: int = Field()
    new_owner_id: str | None = Field(
        default_factory=uuid.uuid4, max_length=36, nullable=False
    )
    created_on: datetime.datetime | None = Field(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_on: datetime.datetime | None = Field(nullable=True, default=None)
    # owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: int


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
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str = Field(max_length=4000)
    new_password: str = Field(min_length=8, max_length=128)


class Media(SQLModel, table=True):
    id: str = Field(default_factory=uuid.uuid4, primary_key=True, max_length=36)
    name: str = Field(max_length=200)
    uploaded_on: datetime.datetime
    created_on: datetime.datetime
    updated_on: datetime.datetime


class Test(SQLModel, table=True):
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


class Member(DefaultBase, table=True):
    first_name: str = Field(max_length=200, nullable=False)
    last_name: str = Field(max_length=200, nullable=False)
    birthday: datetime.datetime = Field(nullable=False)
    wedding_anniversary: datetime.datetime = Field(nullable=True)
    baptism_date: datetime.datetime


class ChurchService(DefaultBase, table=True):
    service_date: datetime.datetime = Field(nullable=False)
    speaker: str = Field(max_length=200, nullable=True)
    service_title: Optional[str] = Field(max_length=200, nullable=True)
    file_location: Optional[str] = Field(max_length=1000, nullable=True)
    edited: bool = Field(nullable=False, default=False)
    uploaded: bool = Field(nullable=False, default=False)


class VideoUpload(DefaultBase, table=True):
    upload_location: str = Field(max_length=1000)
    upload_name: str = Field(max_length=1000)


class Announcement(DefaultBase, table=True):
    sender: str = Field(max_length=200)
    recipients: str = Field(max_length=4000)
    message: str = Field(max_length=4000)

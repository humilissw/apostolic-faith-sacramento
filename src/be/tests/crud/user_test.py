import pytest
from fastapi.encoders import jsonable_encoder
from sqlmodel import select

from app import crud
from app.core.security import verify_password
from app.models import User, UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


@pytest.mark.asyncio
async def test_create_user(db_session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


@pytest.mark.asyncio
async def test_authenticate_user(db_session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    authenticated_user = await crud.authenticate(session=db_session, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


@pytest.mark.asyncio
async def test_not_authenticate_user(db_session) -> None:
    email = random_email()
    password = random_lower_string()
    user = await crud.authenticate(session=db_session, email=email, password=password)
    assert user is None


@pytest.mark.asyncio
async def test_check_if_user_is_active(db_session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    assert user.is_active is True


@pytest.mark.asyncio
async def test_check_if_user_is_active_inactive(db_session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = await crud.create_user(session=db_session, user_create=user_in)
    assert user.is_active


@pytest.mark.asyncio
async def test_check_if_user_is_superuser(db_session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = await crud.create_user(session=db_session, user_create=user_in)
    assert user.is_superuser is True


@pytest.mark.asyncio
async def test_check_if_user_is_superuser_normal_user(db_session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_get_user(db_session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = await crud.create_user(session=db_session, user_create=user_in)
    result = await db_session.execute(select(User).where(User.id == user.id))
    user_2 = result.scalar()
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


@pytest.mark.asyncio
async def test_update_user(db_session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = await crud.create_user(session=db_session, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
        await crud.update_user(session=db_session, db_user=user, user_in=user_in_update)
    result = await db_session.execute(select(User).where(User.id == user.id))
    user_2 = result.scalar()
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)

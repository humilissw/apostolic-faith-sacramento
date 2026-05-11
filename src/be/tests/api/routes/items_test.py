import pytest
from sqlalchemy import select

from app.config import settings
from app.core.security import get_password_hash
from app.crud import create_user
from app.models import User, UserCreate, UserScope

from tests.utils.item import create_random_item


@pytest.mark.asyncio
async def test_create_item(client, superuser_token_headers) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = await client.post(
        "/api/v1/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


@pytest.mark.asyncio
async def test_read_item(client, superuser_token_headers, db_session) -> None:
    item = await create_random_item(db_session)
    response = await client.get(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id


@pytest.mark.asyncio
async def test_read_item_not_found(client, superuser_token_headers) -> None:
    response = await client.get(
        "/api/v1/items/999999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_read_item_not_enough_permissions(client, db_session) -> None:
    """A user with api:all scope but not owner gets 400 from endpoint logic."""
    # Create a user with api:all scope so scope check passes,
    # but the user is not the item owner so endpoint logic returns 400.
    email = "api_all_test@example.com"
    statement = select(User).where(User.email == email)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )
    user.hashed_password = get_password_hash("testpassword123")
    db_session.add(user)
    await db_session.commit()
    # Grant api:all so scope check passes
    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "api:all")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="api:all"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    item = await create_random_item(db_session)
    response = await client.get(
        f"/api/v1/items/{item.id}",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


@pytest.mark.asyncio
async def test_read_items(client, superuser_token_headers, db_session) -> None:
    await create_random_item(db_session)
    await create_random_item(db_session)
    response = await client.get(
        "/api/v1/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


@pytest.mark.asyncio
async def test_update_item(client, superuser_token_headers, db_session) -> None:
    item = await create_random_item(db_session)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id


@pytest.mark.asyncio
async def test_update_item_not_found(client, superuser_token_headers) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        "/api/v1/items/999999999",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_update_item_not_enough_permissions(client, db_session) -> None:
    """A user with api:all scope but not owner gets 400 from endpoint logic."""
    email = "update_test@example.com"
    statement = select(User).where(User.email == email)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )
    user.hashed_password = get_password_hash("testpassword123")
    db_session.add(user)
    await db_session.commit()
    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "api:all")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="api:all"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    item = await create_random_item(db_session)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"/api/v1/items/{item.id}",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


@pytest.mark.asyncio
async def test_delete_item(client, superuser_token_headers, db_session) -> None:
    item = await create_random_item(db_session)
    response = await client.delete(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


@pytest.mark.asyncio
async def test_delete_item_not_found(client, superuser_token_headers) -> None:
    response = await client.delete(
        "/api/v1/items/999999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_delete_item_not_enough_permissions(client, db_session) -> None:
    """A user with api:all scope but not owner gets 400 from endpoint logic."""
    email = "delete_test@example.com"
    statement = select(User).where(User.email == email)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )
    user.hashed_password = get_password_hash("testpassword123")
    db_session.add(user)
    await db_session.commit()
    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "api:all")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="api:all"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    item = await create_random_item(db_session)
    response = await client.delete(
        f"/api/v1/items/{item.id}",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"

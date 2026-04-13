import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.item import create_random_item


async def test_create_item(
    client, superuser_token_headers
) -> None:
    data = {"title": "Foo", "description": "Fighters", "new_id": uuid.uuid4()}
    response = client.post(
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


async def test_read_item(
    client, superuser_token_headers, db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = client.get(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


async def test_read_item_not_found(
    client, superuser_token_headers
) -> None:
    response = client.get(
        f"/api/v1/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_read_item_not_enough_permissions(
    client, normal_user_token_headers, db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = client.get(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_read_items(
    client, superuser_token_headers, db: AsyncSession
) -> None:
    await create_random_item(db)
    await create_random_item(db)
    response = client.get(
        "/api/v1/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


async def test_update_item(
    client, superuser_token_headers, db: AsyncSession
) -> None:
    item = await create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


async def test_update_item_not_found(
    client, superuser_token_headers
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"/api/v1/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_update_item_not_enough_permissions(
    client, normal_user_token_headers, db: AsyncSession
) -> None:
    item = await create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_delete_item(
    client, superuser_token_headers, db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = client.delete(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


async def test_delete_item_not_found(
    client, superuser_token_headers
) -> None:
    response = client.delete(
        f"/api/v1/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_delete_item_not_enough_permissions(
    client, normal_user_token_headers, db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = client.delete(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
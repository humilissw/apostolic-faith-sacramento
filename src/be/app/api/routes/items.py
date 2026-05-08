from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/",
    response_model=ItemsPublic,
    dependencies=[require_scope("api:all")],
)
async def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = (await session.execute(count_statement)).scalar_one()
        statement = select(Item).offset(skip).limit(limit)
        items = (await session.execute(statement)).scalars().all()
    else:
        count_statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
        )
        count = (await session.execute(count_statement)).scalar_one()
        statement = select(Item).where(Item.owner_id == current_user.id).offset(skip).limit(limit)
        items = (await session.execute(statement)).scalars().all()

    return ItemsPublic(data=items, count=count)


@router.get(
    "/{id}",
    response_model=ItemPublic,
    dependencies=[require_scope("api:all")],
)
async def read_item(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get item by ID.
    """
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post(
    "/",
    response_model=ItemPublic,
    dependencies=[require_scope("api:all")],
)
async def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = Item.model_validate(
        item_in,
        update={"owner_id": current_user.id, "new_owner_id": current_user.new_id},
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.put(
    "/{id}",
    response_model=ItemPublic,
    dependencies=[require_scope("api:all")],
)
async def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.delete(
    "/{id}",
    dependencies=[require_scope("api:all")],
)
async def delete_item(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an item.
    """
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    await session.delete(item)
    await session.commit()
    return Message(message="Item deleted successfully")

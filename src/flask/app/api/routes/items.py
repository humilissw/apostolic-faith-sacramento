from flask import Blueprint, jsonify
from sqlalchemy import func, select

from app.api.deps import get_current_user, get_db, require_scope
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic

router = Blueprint("items", __name__, url_prefix="/items")


@router.route("/", methods=["GET"])
@require_scope("api:all")
def read_items(skip: int = 0, limit: int = 100):
    session = get_db()
    current_user = get_current_user()
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.execute(count_statement).scalar_one()
        statement = select(Item).offset(skip).limit(limit)
        items = session.execute(statement).scalars().all()
    else:
        count_statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
        )
        count = session.execute(count_statement).scalar_one()
        statement = select(Item).where(Item.owner_id == current_user.id).offset(skip).limit(limit)
        items = session.execute(statement).scalars().all()
    return jsonify(ItemsPublic(data=items, count=count).model_dump())


@router.route("/<int:id>", methods=["GET"])
@require_scope("api:all")
def read_item(id: int):
    session = get_db()
    current_user = get_current_user()
    item = session.get(Item, id)
    if not item:
        return jsonify({"detail": "Item not found"}), 404
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        return jsonify({"detail": "Not enough permissions"}), 400
    return jsonify(ItemPublic.model_validate(item).model_dump())


@router.route("/", methods=["POST"])
@require_scope("api:all")
def create_item():
    from flask import request

    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    item_in = ItemCreate(**data)
    item = Item.model_validate(
        item_in, update={"owner_id": current_user.id, "new_owner_id": current_user.new_id}
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return jsonify(ItemPublic.model_validate(item).model_dump()), 201


@router.route("/<int:id>", methods=["PUT"])
@require_scope("api:all")
def update_item(id: int):
    from flask import request

    session = get_db()
    current_user = get_current_user()
    item = session.get(Item, id)
    if not item:
        return jsonify({"detail": "Item not found"}), 404
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        return jsonify({"detail": "Not enough permissions"}), 400
    update_dict = request.get_json()
    update_data = {k: v for k, v in update_dict.items()}
    item.sqlmodel_update(update_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return jsonify(ItemPublic.model_validate(item).model_dump())


@router.route("/<int:id>", methods=["DELETE"])
@require_scope("api:all")
def delete_item(id: int):
    session = get_db()
    current_user = get_current_user()
    item = session.get(Item, id)
    if not item:
        return jsonify({"detail": "Item not found"}), 404
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        return jsonify({"detail": "Not enough permissions"}), 400
    session.delete(item)
    session.commit()
    return jsonify({"message": "Item deleted successfully"})

"""Private user creation routes."""

from flask import Blueprint, jsonify, request
from pydantic import BaseModel

from app.api.deps import get_current_active_superuser, get_db
from app.models import UserCreate, UserPublic

router = Blueprint("private", __name__, url_prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.route("/users/", methods=["POST"])
def create_user():
    _ = get_current_active_superuser()
    data = request.get_json()
    body = PrivateUserCreate(**data)
    user_create = UserCreate(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        is_active=body.is_verified,
    )
    from app.crud import create_user as crud_create_user

    session = get_db()
    user = crud_create_user(session=session, user_create=user_create)
    return jsonify(UserPublic.model_validate(user.model_dump()).model_dump())

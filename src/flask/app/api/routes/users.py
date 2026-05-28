from flask import Blueprint, jsonify, request

from app.api.deps import (
    get_current_active_superuser,
    get_current_user,
    get_db,
    require_scope,
)
from app.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UserScope,
)
from app import crud
from app.repositories.user_repo import UserRepository
from app.repositories.user_scope_repo import UserScopeRepository
from app.utils import generate_new_account_email, send_email

router = Blueprint("users", __name__, url_prefix="/users")


def _populate_scopes(session, user):
    repo = UserScopeRepository(session)
    scopes = repo.get_scopes(user.id)
    return UserPublic(
        email=user.email,
        is_active=user.is_active,
        id=user.id,
        new_id=user.new_id,
        full_name=user.full_name,
        assigned_scopes=scopes,
    )


@router.route("/", methods=["GET"])
@require_scope("api:all")
def read_users(skip: int = 0, limit: int = 100):
    session = get_db()
    _ = get_current_active_superuser()
    repository = UserRepository(session=session)
    users, total_count = repository.get_all(skip=skip, limit=limit)
    populated = [_populate_scopes(session, u) for u in users]
    return jsonify(UsersPublic(data=populated, count=total_count).model_dump())


@router.route("/", methods=["POST"])
@require_scope("api:all")
def create_user():
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    user_in = UserCreate(**data)
    repository = UserRepository(session=session)
    user = repository.get_by_email(email=user_in.email)
    if user:
        return jsonify({"detail": "The user with this email already exists in the system."}), 400
    user = repository.create(user_create=user_in)
    if user_in.scopes:
        scope_repo = UserScopeRepository(session)
        scope_repo.set_scopes(user.id, user_in.scopes)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email, subject=email_data.subject, html_content=email_data.html_content
        )
    return jsonify(_populate_scopes(session, user).model_dump())


@router.route("/me", methods=["PATCH"])
@require_scope("api:all")
def update_user_me():
    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    user_in = UserUpdateMe(**data)
    repository = UserRepository(session=session)
    if user_in.email:
        existing_user = repository.get_by_email(email=user_in.email)
        if existing_user and existing_user.new_id != current_user.new_id:
            return jsonify({"detail": "User with this email already exists"}), 409
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return jsonify(current_user)


@router.route("/me/password", methods=["PATCH"])
@require_scope("api:all")
def update_password_me():
    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    body = UpdatePassword(**data)
    if not verify_password(body.current_password, current_user.hashed_password):
        return jsonify({"message": "Incorrect password"}), 400
    if body.current_password == body.new_password:
        return jsonify({"message": "New password cannot be the same as the current one"}), 400
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return jsonify({"message": "Password updated successfully"})


@router.route("/me", methods=["GET"])
@require_scope("api:all")
def read_user_me():
    session = get_db()
    current_user = get_current_user()
    return jsonify(_populate_scopes(session, current_user).model_dump())


@router.route("/me", methods=["DELETE"])
@require_scope("api:all")
def delete_user_me():
    session = get_db()
    current_user = get_current_user()
    if current_user.is_superuser:
        return jsonify({"detail": "Super users are not allowed to delete themselves"}), 403
    user_id = str(current_user.id)
    scopes_stmt = (
        __import__("sqlalchemy")
        .select(__import__("sqlalchemy").delete(UserScope))
        .where(UserScope.user_id == user_id)
    )
    session.execute(scopes_stmt)
    session.delete(current_user)
    session.commit()
    return jsonify({"message": "User deleted successfully"})


@router.route("/signup", methods=["POST"])
def register_user():
    session = get_db()
    data = request.get_json()
    user_in = UserRegister(**data)
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        return jsonify({"detail": "The user with this email already exists in the system"}), 400
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return jsonify(user)


@router.route("/admin/<user_id>/scopes", methods=["GET"])
@require_scope("api:all")
def get_user_scopes(user_id: str):
    session = get_db()
    repo = UserScopeRepository(session)
    return jsonify(repo.get_scopes(user_id))


@router.route("/admin/<user_id>/scopes", methods=["PUT"])
@require_scope("api:all")
def set_user_scopes(user_id: str):
    session = get_db()
    scopes = request.get_json()
    repo = UserScopeRepository(session)
    repo.set_scopes(user_id, scopes)
    return jsonify(repo.get_scopes(user_id))


@router.route("/admin/bulk-delete", methods=["POST"])
@require_scope("api:all")
def bulk_delete_users():
    session = get_db()
    data = request.get_json()
    user_ids = data.get("user_ids", [])
    deleted = 0
    for uid in user_ids:
        user = UserRepository(session).get_by_id(uid)
        if user:
            user_id_str = str(user.id)
            items_stmt = (
                __import__("sqlalchemy")
                .select(__import__("sqlalchemy").delete(Item))
                .where(Item.owner_id == user.id)
            )
            session.execute(items_stmt)
            scopes_stmt = (
                __import__("sqlalchemy")
                .select(__import__("sqlalchemy").delete(UserScope))
                .where(UserScope.user_id == user_id_str)
            )
            session.execute(scopes_stmt)
            session.delete(user)
            deleted += 1
    session.commit()
    return jsonify({"message": f"Deleted {deleted} users"})


@router.route("/admin/all", methods=["GET"])
@require_scope("api:all")
def get_all_users():
    session = get_db()
    repository = UserRepository(session=session)
    users, _ = repository.get_all(skip=0, limit=10000)
    populated = [_populate_scopes(session, u) for u in users]
    return jsonify(UsersPublic(data=populated, count=len(populated)).model_dump())


@router.route("/<user_id>", methods=["GET"])
@require_scope("api:all")
def read_user_by_id(user_id: str):
    session = get_db()
    current_user = get_current_user()
    repository = UserRepository(session=session)
    user = repository.get_by_id(user_id=user_id)
    if user is None:
        return jsonify({"detail": "User not found"}), 404
    if user == current_user:
        return jsonify(_populate_scopes(session, user).model_dump())
    if not current_user.is_superuser:
        return jsonify({"detail": "The user doesn't have enough privileges"}), 403
    return jsonify(_populate_scopes(session, user).model_dump())


@router.route("/<user_id>", methods=["PATCH"])
@require_scope("api:all")
def update_user(user_id: str):
    session = get_db()
    data = request.get_json()
    user_in = UserUpdate(**data)
    repository = UserRepository(session=session)
    db_user = repository.get_by_id(user_id=user_id)
    if not db_user:
        return jsonify({"detail": "The user with this id does not exist in the system"}), 404
    if user_in.email:
        existing_user = repository.get_by_email(email=user_in.email)
        if existing_user and existing_user.id != user_id:
            return jsonify({"detail": "User with this email already exists"}), 409
    db_user = repository.update(db_user=db_user, user_in=user_in)
    return jsonify(_populate_scopes(session, db_user).model_dump())


@router.route("/<user_id>", methods=["DELETE"])
@require_scope("api:all")
def delete_user(user_id: str):
    session = get_db()
    current_user = get_current_user()
    repository = UserRepository(session=session)
    user = repository.get_by_id(user_id=user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    if user == current_user:
        return jsonify({"detail": "Super users are not allowed to delete themselves"}), 403
    user_id_str = str(user.id)
    items_stmt = (
        __import__("sqlalchemy")
        .select(__import__("sqlalchemy").delete(Item))
        .where(Item.owner_id == user_id)
    )
    session.execute(items_stmt)
    scopes_stmt = (
        __import__("sqlalchemy")
        .select(__import__("sqlalchemy").delete(UserScope))
        .where(UserScope.user_id == user_id_str)
    )
    session.execute(scopes_stmt)
    session.delete(user)
    session.commit()
    return jsonify({"message": "User deleted successfully"})


class UpdatePassword:
    pass

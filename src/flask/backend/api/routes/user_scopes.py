"""Routes for managing per-user scopes (claims)."""

from flask import Blueprint, jsonify, request

from backend.api.deps import get_current_active_superuser, get_db
from backend.repositories.user_scope_repo import UserScopeRepository

router = Blueprint("user_scopes", __name__)


@router.route("/users/admin/<user_id>/scopes")
def get_user_scopes(user_id: str):
    _tag = "user-scopes"
    session = get_db()
    _ = get_current_active_superuser()
    repo = UserScopeRepository(session)
    scopes = repo.get_scopes(user_id)
    return jsonify(scopes)


@router.route("/users/admin/<user_id>/scopes", methods=["PUT"])
def set_user_scopes(user_id: str):
    _tag = "user-scopes"
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    scopes = data.get("scopes", [])
    repo = UserScopeRepository(session)
    repo.set_scopes(user_id, scopes)
    scopes = repo.get_scopes(user_id)
    return jsonify(scopes)


@router.route("/users/admin/<user_id>", methods=["DELETE"])
def remove_all_user_scopes(user_id: str):
    _tag = "user-scopes"
    session = get_db()
    _ = get_current_active_superuser()
    repo = UserScopeRepository(session)
    repo.set_scopes(user_id, [])
    return jsonify({}), 204

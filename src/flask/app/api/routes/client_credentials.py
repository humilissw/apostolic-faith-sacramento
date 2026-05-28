"""Routes for managing OAuth2 client credentials."""

from flask import Blueprint, jsonify, request

from app.api.deps import get_current_active_superuser, get_db
from app.models import (
    ClientCredentials,
    ClientCredentialsCreate,
    ClientCredentialsPublic,
    ClientCredentialsUpdate,
)
from sqlalchemy import select

router = Blueprint("client_credentials", __name__, url_prefix="/admin/client-credentials")


def _to_public(cc: ClientCredentials) -> ClientCredentialsPublic:
    return ClientCredentialsPublic(
        id=cc.id,
        client_id=cc.client_id,
        scopes=cc.scopes.split(",") if cc.scopes else [],
        is_active=cc.is_active,
    )


@router.route("/", methods=["GET"])
def list_client_credentials():
    session = get_db()
    _ = get_current_active_superuser()
    result = session.execute(select(ClientCredentials))
    return jsonify([cc.model_dump() for cc in result.scalars().all()])


@router.route("/", methods=["POST"])
def create_client_credentials():
    import secrets
    from app.core.security import get_password_hash

    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    body = ClientCredentialsCreate(**data)
    result = session.execute(
        select(ClientCredentials).where(ClientCredentials.client_id == body.client_id)
    )
    if result.scalar_one_or_none():
        return jsonify({"detail": "Client ID already exists"}), 409
    client_secret = secrets.token_urlsafe(32)
    hashed = get_password_hash(client_secret)
    db_cc = ClientCredentials(
        client_id=body.client_id, client_secret_hash=hashed, scopes=",".join(body.scopes)
    )
    session.add(db_cc)
    session.commit()
    session.refresh(db_cc)
    return (
        jsonify(
            ClientCredentialsPublic(
                id=db_cc.id,
                client_id=db_cc.client_id,
                scopes=db_cc.scopes.split(",") if db_cc.scopes else [],
                is_active=db_cc.is_active,
            ).model_dump()
        ),
        201,
    )


@router.route("/<cc_id>", methods=["PATCH"])
def update_client_credentials(cc_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    body = ClientCredentialsUpdate(**data) if data else {}
    result = session.execute(select(ClientCredentials).where(ClientCredentials.id == cc_id))
    cc = result.scalar_one_or_none()
    if not cc:
        return jsonify({"detail": "Client credentials not found"}), 404
    if body.get("scopes") is not None:
        cc.scopes = ",".join(body["scopes"])
    if body.get("is_active") is not None:
        cc.is_active = body["is_active"]
    session.commit()
    session.refresh(cc)
    return jsonify(
        ClientCredentialsPublic(
            id=cc.id,
            client_id=cc.client_id,
            scopes=cc.scopes.split(",") if cc.scopes else [],
            is_active=cc.is_active,
        ).model_dump()
    )


@router.route("/<cc_id>", methods=["DELETE"])
def delete_client_credentials(cc_id: str):
    session = get_db()
    _ = get_current_active_superuser()
    result = session.execute(select(ClientCredentials).where(ClientCredentials.id == cc_id))
    cc = result.scalar_one_or_none()
    if not cc:
        return jsonify({"detail": "Client credentials not found"}), 404
    session.delete(cc)
    session.commit()
    return jsonify({}), 204

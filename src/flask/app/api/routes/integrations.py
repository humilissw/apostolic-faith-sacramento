"""Routes for third-party integration management."""

from flask import Blueprint, jsonify, request

from app.api.deps import get_current_user, get_db, require_scope
from app.models import IntegrationConfig
from app.repositories.integration_repo import IntegrationConfigRepository
from app.requests.integration_request import (
    CredentialUpdate,
    IntegrationCreate,
    IntegrationUpdate,
    TestConnectionRequest,
)
from app.responses.integration_response import (
    IntegrationConfigPublic,
    IntegrationConfigPublicWithCreds,
    IntegrationsPublic,
    TestConnectionResponse,
)
from app.services.integration_service import KNOWN_INTEGRATIONS, IntegrationService

router = Blueprint("integrations", __name__, url_prefix="/integrations")


def _get_service(session):
    return IntegrationService(IntegrationConfigRepository(session))


def _mask_credentials(creds):
    if not creds:
        return {}
    return {
        field: f"****{value[-4:]}" if len(value) > 4 else "****" for field, value in creds.items()
    }


@router.route("/", methods=["GET"])
@require_scope("integrations:admin")
def list_integrations(skip: int = 0, limit: int = 100):
    session = get_db()
    _ = get_current_user()
    service = _get_service(session)
    items, total = service.get_all(skip, limit)
    integrations = []
    for item in items:
        try:
            is_valid = IntegrationConfigPublic.model_validate(item.model_dump())
            if is_valid:
                integrations.append(is_valid)
        except Exception as error:
            print(error)
    return jsonify(IntegrationsPublic(data=integrations, count=total).model_dump())


@router.route("/status")
def get_integrations_status():
    session = get_db()
    from sqlalchemy import select

    statement = select(IntegrationConfig)
    result = session.execute(statement)
    integrations = list(result.scalars().all())
    return jsonify({i.type: {"enabled": i.enabled, "status": i.status} for i in integrations})


@router.route("/<integration_id>", methods=["GET"])
@require_scope("integrations:admin")
def get_integration(integration_id: str):
    session = get_db()
    _ = get_current_user()
    service = _get_service(session)
    integration = service.get_by_id(integration_id)
    if not integration:
        return jsonify({"detail": "Integration not found"}), 404
    creds = service.get_credentials(integration)
    return jsonify(
        IntegrationConfigPublicWithCreds(
            **IntegrationConfigPublic.model_validate(integration.model_dump()).model_dump(),
            credential_fields=_mask_credentials(creds),
        ).model_dump()
    )


@router.route("/", methods=["POST"])
@require_scope("integrations:admin")
def create_integration():
    session = get_db()
    _ = get_current_user()
    data = request.get_json()
    integration_in = IntegrationCreate(**data)
    service = _get_service(session)
    existing = service.get_by_type(integration_in.type)
    if existing:
        return jsonify({"detail": f"Integration type '{integration_in.type}' already exists"}), 409
    meta = KNOWN_INTEGRATIONS.get(integration_in.type, {})
    display_name = integration_in.display_name or meta.get("display_name", integration_in.type)
    icon = integration_in.icon or meta.get("icon", "Plug")
    integration = service.create(
        type=integration_in.type,
        display_name=display_name,
        icon=icon,
        enabled=integration_in.enabled,
        config_json=integration_in.config_json,
        credentials=integration_in.credentials,
    )
    creds = service.get_credentials(integration)
    return (
        jsonify(
            IntegrationConfigPublicWithCreds(
                **IntegrationConfigPublic.model_validate(integration.model_dump()).model_dump(),
                credential_fields=_mask_credentials(creds),
            ).model_dump()
        ),
        201,
    )


@router.route("/<integration_id>", methods=["PUT"])
@require_scope("integrations:admin")
def update_integration(integration_id: str):
    session = get_db()
    _ = get_current_user()
    data = request.get_json()
    integration_in = IntegrationUpdate(**data)
    service = _get_service(session)
    integration = service.get_by_id(integration_id)
    if not integration:
        return jsonify({"detail": "Integration not found"}), 404
    update_data = integration_in.model_dump(exclude_unset=True)
    updated = service.update(integration, update_data)
    creds = service.get_credentials(updated)
    return jsonify(
        IntegrationConfigPublicWithCreds(
            **IntegrationConfigPublic.model_validate(updated.model_dump()).model_dump(),
            credential_fields=_mask_credentials(creds),
        ).model_dump()
    )


@router.route("/<integration_id>/credentials", methods=["PATCH"])
@require_scope("integrations:admin")
def update_credentials(integration_id: str):
    session = get_db()
    _ = get_current_user()
    data = request.get_json()
    cred_in = CredentialUpdate(**data)
    service = _get_service(session)
    integration = service.get_by_id(integration_id)
    if not integration:
        return jsonify({"detail": "Integration not found"}), 404
    updated = service.update_credentials(integration, cred_in.credentials)
    creds = service.get_credentials(updated)
    return jsonify(
        IntegrationConfigPublicWithCreds(
            **IntegrationConfigPublic.model_validate(updated.model_dump()).model_dump(),
            credential_fields=_mask_credentials(creds),
        ).model_dump()
    )


@router.route("/<integration_id>", methods=["DELETE"])
@require_scope("integrations:admin")
def delete_integration(integration_id: str):
    session = get_db()
    _ = get_current_user()
    service = _get_service(session)
    integration = service.get_by_id(integration_id)
    if not integration:
        return jsonify({"detail": "Integration not found"}), 404
    service.delete(integration)
    return jsonify({"message": "Integration deleted"})


@router.route("/test-connection", methods=["POST"])
@require_scope("integrations:admin")
def test_connection():
    session = get_db()
    _ = get_current_user()
    data = request.get_json()
    test_in = TestConnectionRequest(**data)
    service = _get_service(session)
    config = None
    if test_in.config_json:
        import json

        try:
            config = json.loads(test_in.config_json)
        except json.JSONDecodeError:
            return jsonify({"detail": "Invalid config_json"}), 400
    result = service.test_connection(test_in.type, test_in.credentials, config)
    return jsonify(TestConnectionResponse(**result).model_dump())


@router.route("/sync-status/<integration_id>", methods=["POST"])
@require_scope("integrations:admin")
def sync_status(integration_id: str):
    session = get_db()
    _ = get_current_user()
    service = _get_service(session)
    integration = service.get_by_id(integration_id)
    if not integration:
        return jsonify({"detail": "Integration not found"}), 404
    updated = service.sync_status(integration, "connected")
    return jsonify(IntegrationConfigPublic.model_validate(updated.model_dump()).model_dump())


@router.route("/pre-seed", methods=["POST"])
@require_scope("integrations:admin")
def pre_seed_integrations():
    session = get_db()
    _ = get_current_user()
    service = _get_service(session)
    created = []
    for type_id, meta in KNOWN_INTEGRATIONS.items():
        existing = service.get_by_type(type_id)
        if not existing:
            created.append(
                service.create(
                    type=type_id,
                    display_name=meta["display_name"],
                    icon=meta["icon"],
                    enabled=False,
                    config_json=None,
                    credentials={},
                )
            )
    items, total = service.get_all()
    return jsonify(
        IntegrationsPublic(
            data=[IntegrationConfigPublic.model_validate(i.model_dump()) for i in items],
            count=total,
        ).model_dump()
    )

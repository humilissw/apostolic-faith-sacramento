"""Routes for third-party integration management."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, SessionDep, require_scope
from app.models import IntegrationConfig, Message
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
from app.services.integration_service import (
    KNOWN_INTEGRATIONS,
    IntegrationService,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _get_service(session) -> IntegrationService:
    return IntegrationService(IntegrationConfigRepository(session))


def _mask_credentials(creds: dict[str, str] | None) -> dict[str, str]:
    if not creds:
        return {}
    return {
        field: f"****{value[-4:]}" if len(value) > 4 else "****" for field, value in creds.items()
    }


@router.get(
    "/",
    response_model=IntegrationsPublic,
    dependencies=[require_scope("integrations:admin")],
)
async def list_integrations(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> IntegrationsPublic:
    """List all integration configurations (superuser only)."""
    service = _get_service(session)
    items, total = await service.get_all(skip, limit)
    integrations = []
    for item in items:
        try:
            is_valid = IntegrationConfigPublic.model_validate(item.model_dump())
            if is_valid:
                integrations.append(is_valid)
        except Exception as error:
            print(error)
    return IntegrationsPublic(
        data=integrations,
        count=total,
    )


@router.get("/status", response_model=dict)
async def get_integrations_status(session: SessionDep) -> dict:
    """Get summary of all integrations (public, no auth required)."""
    statement = select(IntegrationConfig)
    result = await session.execute(statement)
    integrations = list(result.scalars().all())
    return {i.type: {"enabled": i.enabled, "status": i.status} for i in integrations}


@router.get(
    "/{integration_id}",
    response_model=IntegrationConfigPublicWithCreds,
    dependencies=[require_scope("integrations:admin")],
)
async def get_integration(
    integration_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> IntegrationConfigPublicWithCreds:
    """Get a single integration with masked credentials (superuser only)."""
    service = _get_service(session)
    integration = await service.get_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    creds = await service.get_credentials(integration)
    return IntegrationConfigPublicWithCreds(
        **IntegrationConfigPublic.model_validate(integration.model_dump()).model_dump(),
        credential_fields=_mask_credentials(creds),
    )


@router.post(
    "/",
    response_model=IntegrationConfigPublicWithCreds,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_scope("integrations:admin")],
)
async def create_integration(
    integration_in: IntegrationCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> IntegrationConfigPublicWithCreds:
    """Create a new integration with encrypted credentials (superuser only)."""
    service = _get_service(session)

    # Check for duplicate type
    existing = await service.get_by_type(integration_in.type)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Integration type '{integration_in.type}' already exists",
        )

    # Use KNOWN_INTEGRATIONS defaults if not provided
    meta = KNOWN_INTEGRATIONS.get(integration_in.type, {})
    display_name = integration_in.display_name or meta.get("display_name", integration_in.type)
    icon = integration_in.icon or meta.get("icon", "Plug")

    integration = await service.create(
        type=integration_in.type,
        display_name=display_name,
        icon=icon,
        enabled=integration_in.enabled,
        config_json=integration_in.config_json,
        credentials=integration_in.credentials,
    )

    creds = await service.get_credentials(integration)
    return IntegrationConfigPublicWithCreds(
        **IntegrationConfigPublic.model_validate(integration.model_dump()).model_dump(),
        credential_fields=_mask_credentials(creds),
    )


@router.put(
    "/{integration_id}",
    response_model=IntegrationConfigPublicWithCreds,
    dependencies=[require_scope("integrations:admin")],
)
async def update_integration(
    integration_id: str,
    integration_in: IntegrationUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> IntegrationConfigPublicWithCreds:
    """Update an integration (superuser only)."""
    service = _get_service(session)
    integration = await service.get_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    update_data = integration_in.model_dump(exclude_unset=True)
    updated = await service.update(integration, update_data)

    creds = await service.get_credentials(updated)
    return IntegrationConfigPublicWithCreds(
        **IntegrationConfigPublic.model_validate(updated.model_dump()).model_dump(),
        credential_fields=_mask_credentials(creds),
    )


@router.patch(
    "/{integration_id}/credentials",
    response_model=IntegrationConfigPublicWithCreds,
    dependencies=[require_scope("integrations:admin")],
)
async def update_credentials(
    integration_id: str,
    cred_in: CredentialUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> IntegrationConfigPublicWithCreds:
    """Update only the credentials for an integration (superuser only)."""
    service = _get_service(session)
    integration = await service.get_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    updated = await service.update_credentials(integration, cred_in.credentials)
    creds = await service.get_credentials(updated)
    return IntegrationConfigPublicWithCreds(
        **IntegrationConfigPublic.model_validate(updated.model_dump()).model_dump(),
        credential_fields=_mask_credentials(creds),
    )


@router.delete(
    "/{integration_id}",
    response_model=Message,
    dependencies=[require_scope("integrations:admin")],
)
async def delete_integration(
    integration_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """Delete an integration (superuser only)."""
    service = _get_service(session)
    integration = await service.get_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    await service.delete(integration)
    return Message(message="Integration deleted")


@router.post(
    "/test-connection",
    response_model=TestConnectionResponse,
    dependencies=[require_scope("integrations:admin")],
)
async def test_connection(
    test_in: TestConnectionRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> TestConnectionResponse:
    """Test connection for an integration type (superuser only)."""
    service = _get_service(session)
    config = None
    if test_in.config_json:
        import json

        try:
            config = json.loads(test_in.config_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid config_json")

    result = await service.test_connection(test_in.type, test_in.credentials, config)
    return TestConnectionResponse(**result)


@router.post(
    "/sync-status/{integration_id}",
    response_model=IntegrationConfigPublic,
    dependencies=[require_scope("integrations:admin")],
)
async def sync_status(
    integration_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> IntegrationConfigPublic:
    """Manually update the connection status of an integration (superuser only)."""
    service = _get_service(session)
    integration = await service.get_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    updated = await service.sync_status(integration, "connected")
    return IntegrationConfigPublic.model_validate(updated.model_dump())


@router.post(
    "/pre-seed",
    response_model=IntegrationsPublic,
    dependencies=[require_scope("integrations:admin")],
)
async def pre_seed_integrations(
    session: SessionDep,
    current_user: CurrentUser,
) -> IntegrationsPublic:
    """Create placeholder entries for all known integration types (superuser only)."""
    service = _get_service(session)
    created = []

    for type_id, meta in KNOWN_INTEGRATIONS.items():
        existing = await service.get_by_type(type_id)
        if not existing:
            created.append(
                await service.create(
                    type=type_id,
                    display_name=meta["display_name"],
                    icon=meta["icon"],
                    enabled=False,
                    config_json=None,
                    credentials={},
                )
            )

    items, total = await service.get_all()
    return IntegrationsPublic(
        data=[IntegrationConfigPublic.model_validate(i.model_dump()) for i in items],
        count=total,
    )

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select

from app.config import settings
from app.core.security import get_password_hash
from app.crud import create_user
from app.models import DonationConfig, Payment, User, UserCreate
from app.api.routes import payments as payments_route


@pytest.fixture(scope="function")
async def payment_user(client, db_session) -> str:
    """Create a test user and return their ID."""
    import uuid

    email = f"payment_test_{uuid.uuid4().hex[:8]}@test.com"
    user = await create_user(
        session=db_session,
        user_create=UserCreate(email=email, password="testpass123"),
    )
    return user.id


@pytest.fixture(scope="function")
async def payment_token(client, db_session, payment_user) -> dict[str, str]:
    """Login as the payment test user and return auth headers."""
    statement = select(User).where(User.id == payment_user)
    user = (await db_session.execute(statement)).scalar_one()
    user.hashed_password = get_password_hash("testpass123")
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": user.email, "password": "testpass123"},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _make_webhook_mock(event_type, **kwargs):
    """Return a function that returns webhook data based on the incoming event type."""
    defaults = {
        "payment_intent.succeeded": {
            "type": "payment_intent.succeeded",
            "payment_intent_id": "pi_test123",
            "amount_cents": 5000,
            "status": "succeeded",
            "receipt_url": "https://stripe.com/receipt/123",
            "donor_email": "test@test.com",
            "donor_name": "Test Donor",
        },
        "payment_intent.payment_failed": {
            "type": "payment_intent.payment_failed",
            "payment_intent_id": "pi_failed123",
            "amount_cents": 3000,
            "status": "failed",
            "donor_email": "test@test.com",
            "donor_name": "Test Donor",
        },
        "checkout.session.completed": {
            "type": "checkout.session.completed",
            "payment_intent_id": "pi_web123",
        },
    }

    def handler(*args, **kwargs):
        body = args[1] if len(args) > 1 else kwargs.get("body", "")
        if isinstance(body, str):
            try:
                evt = json.loads(body)
                actual_type = evt.get("type", event_type)
            except json.JSONDecodeError:
                actual_type = event_type
        else:
            actual_type = event_type
        return defaults.get(actual_type, {"type": actual_type, **kwargs})

    return AsyncMock(side_effect=handler)


@pytest.fixture(autouse=True)
def mock_payment_service():
    """Mock PaymentService to avoid real Stripe calls."""
    mock_service = MagicMock()
    mock_service.create_payment_intent = AsyncMock(
        return_value={
            "client_secret": "cs_test123",
            "payment_intent_id": "pi_test123",
        }
    )
    mock_service.create_checkout_session = AsyncMock(
        return_value={
            "client_secret": "cs_test456",
            "type": "checkout",
            "checkout_url": "https://checkout.stripe.com/test456",
        }
    )
    mock_service.handle_webhook = _make_webhook_mock("payment_intent.succeeded")

    original_service = payments_route.payment_service
    payments_route.payment_service = mock_service
    yield mock_service
    payments_route.payment_service = original_service


@pytest.mark.asyncio
async def test_create_payment_intent(
    client, payment_token, db_session, mock_payment_service
) -> None:
    response = await client.post(
        "/api/v1/payments/create-intent",
        headers=payment_token,
        json={"amount_cents": 5000, "currency": "usd", "frequency": "one_time"},
    )
    assert response.status_code == 201
    content = response.json()
    assert "payment_intent_id" in content
    assert "client_secret" in content
    mock_payment_service.create_payment_intent.assert_called_once()


@pytest.mark.asyncio
async def test_create_payment_intent_validation(client, payment_token) -> None:
    response = await client.post(
        "/api/v1/payments/create-intent",
        headers=payment_token,
        json={"amount_cents": -1, "currency": "usd", "frequency": "one_time"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_subscription(client, payment_token, mock_payment_service) -> None:
    response = await client.post(
        "/api/v1/payments/create-subscription",
        headers=payment_token,
        json={"amount_cents": 1000, "currency": "usd", "frequency": "recurring"},
    )
    assert response.status_code == 201
    content = response.json()
    assert "checkout_url" in content
    mock_payment_service.create_checkout_session.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_payment_succeeded(client, payment_token) -> None:
    mock_event = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_webhook123",
                "amount": 5000,
                "status": "succeeded",
                "receipt_url": "https://stripe.com/receipt/123",
                "metadata": {"donor_email": "test@test.com", "donor_name": "Test Donor"},
            }
        },
    }

    response = await client.post(
        "/api/v1/payments/webhook",
        headers=payment_token,
        data=json.dumps(mock_event),
    )
    assert response.status_code == 200
    assert "succeeded" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_webhook_payment_failed(client, payment_token) -> None:
    mock_event = {
        "type": "payment_intent.payment_failed",
        "data": {"object": {"id": "pi_failed123", "status": "failed"}},
    }

    response = await client.post(
        "/api/v1/payments/webhook",
        headers=payment_token,
        data=json.dumps(mock_event),
    )
    assert response.status_code == 200
    assert "failed" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_webhook_checkout_completed(client, payment_token) -> None:
    mock_event = {
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_web123", "payment_intent": "pi_web123"}},
    }

    response = await client.post(
        "/api/v1/payments/webhook",
        headers=payment_token,
        data=json.dumps(mock_event),
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_unknown_event(client, payment_token) -> None:
    mock_event = {"type": "invoice.payment_succeeded", "data": {"object": {}}}

    response = await client.post(
        "/api/v1/payments/webhook",
        headers=payment_token,
        data=json.dumps(mock_event),
    )
    assert response.status_code == 200
    assert "ignored" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_get_user_payments(client, payment_token, db_session, payment_user) -> None:
    statement = select(User).where(User.id == payment_user)
    user = (await db_session.execute(statement)).scalar_one()

    pay = Payment(
        amount_cents=1000,
        currency="usd",
        status="pending",
        stripe_payment_intent_id="pi_test_user_payments",
        donor_email=user.email,
        donor_name=user.full_name,
    )
    db_session.add(pay)
    await db_session.commit()

    response = await client.get("/api/v1/payments/", headers=payment_token)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1


@pytest.mark.asyncio
async def test_get_payment_config(client, db_session) -> None:
    config = DonationConfig(
        label="Small Donation",
        amount_cents=1000,
        is_default=True,
        frequency="one_time",
    )
    db_session.add(config)
    await db_session.commit()

    response = await client.get("/api/v1/payments/config")
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    assert any(item["label"] == "Small Donation" for item in content["data"])


@pytest.mark.asyncio
async def test_get_single_payment_found(client, payment_token, db_session, payment_user) -> None:
    statement = select(User).where(User.id == payment_user)
    user = (await db_session.execute(statement)).scalar_one()

    pay = Payment(
        amount_cents=1000,
        currency="usd",
        status="pending",
        stripe_payment_intent_id="pi_test_user_payments",
        donor_email=user.email,
        donor_name=user.full_name,
    )
    db_session.add(pay)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/payments/{pay.id}",
        headers=payment_token,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(pay.id)


@pytest.mark.asyncio
async def test_get_payment_not_found(client, payment_token) -> None:
    import uuid

    fake_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/v1/payments/{fake_id}",
        headers=payment_token,
    )
    assert response.status_code == 404

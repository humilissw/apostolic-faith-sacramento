from typing import Any

import logging
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import CurrentUser, SessionDep
from app.models import DonationConfig, Message
from app.repositories.payment_repo import PaymentRepository
from app.requests.payment_request import PaymentCreate
from app.responses.payment_response import (
    CheckoutSessionResponse,
    DonationConfigPublic,
    DonationConfigsPublic,
    PaymentIntentResponse,
    PaymentPublic,
    PaymentsPublic,
)
from app.services.payment_service import PaymentService, extract_donor_info_from_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()

# Max donation amount: $10,000 (prevents abuse/tampering)
MAX_DONATION_CENTS = 10_000 * 100  # $10,000


@router.post(
    "/create-intent",
    response_model=PaymentIntentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_intent_endpoint(
    payment_in: PaymentCreate,
    session: SessionDep,
    request: Request,
) -> Any:
    """Create a Stripe PaymentIntent for a one-time donation."""
    # Server-side amount validation (prevents client tampering)
    if payment_in.amount_cents > MAX_DONATION_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Donation amount exceeds maximum allowed (${MAX_DONATION_CENTS // 100:,})",
        )

    # Validate that the amount matches a configured donation preset (if configs exist)
    if not await _check_amount_in_config(session, payment_in.amount_cents):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donation amount must match a configured preset",
        )

    # Extract donor info from authenticated request (shared helper)
    email, _ = await extract_donor_info_from_request(request)

    result = await payment_service.create_payment_intent(
        amount_cents=payment_in.amount_cents,
        currency=payment_in.currency,
        donor_email=email if not payment_in.donor_email else payment_in.donor_email,
        donor_name=payment_in.donor_name,
    )

    # Audit log
    _log_payment_attempt(request, payment_in.amount_cents, email or payment_in.donor_email)

    # Persist pending payment record
    repository = PaymentRepository(session=session)
    await repository.create(
        {
            "amount_cents": payment_in.amount_cents,
            "currency": payment_in.currency,
            "status": "pending",
            "stripe_payment_intent_id": result["payment_intent_id"],
            "donor_email": email or payment_in.donor_email,
            "donor_name": payment_in.donor_name,
        }
    )
    return PaymentIntentResponse(**result)


@router.post(
    "/create-subscription",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription_endpoint(
    payment_in: PaymentCreate,
    session: SessionDep,
    request: Request,
) -> Any:
    """Create a Stripe Checkout Session for a recurring donation."""
    if payment_in.amount_cents > MAX_DONATION_CENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Donation amount exceeds maximum allowed (${MAX_DONATION_CENTS // 100:,})",
        )

    if not await _check_amount_in_config(session, payment_in.amount_cents):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donation amount must match a configured preset",
        )

    email, _ = await extract_donor_info_from_request(request)

    result = await payment_service.create_checkout_session(
        amount_cents=payment_in.amount_cents,
        currency=payment_in.currency,
        donor_email=email if not payment_in.donor_email else payment_in.donor_email,
        donor_name=payment_in.donor_name,
        recurring=True,
    )

    _log_payment_attempt(request, payment_in.amount_cents, email or payment_in.donor_email)

    repository = PaymentRepository(session=session)
    checkout_session_id = (
        result.get("checkout_url", "").split("/")[-1] if result.get("checkout_url") else ""
    )
    await repository.create(
        {
            "amount_cents": payment_in.amount_cents,
            "currency": payment_in.currency,
            "status": "pending",
            "stripe_payment_intent_id": checkout_session_id,
            "donor_email": email or payment_in.donor_email,
            "donor_name": payment_in.donor_name,
        }
    )
    return CheckoutSessionResponse(**result)


@router.post("/webhook")
async def webhook_endpoint(request: Request, session: SessionDep) -> Message:
    """Handle Stripe webhook events."""
    body = await request.body()
    signature = request.headers.get("stripe-signature", "")

    # Audit log webhook receipt
    ip_address = request.client.host if request.client else "unknown"
    logger.info(
        "Webhook received from %s | signature=%s",
        ip_address,
        signature[:50] if signature else "none",
    )

    # Bind session for credential resolution and delegate verification + routing to service
    payment_service._session = session
    event_data = await payment_service.handle_webhook(body.decode(), signature)

    repository = PaymentRepository(session=session)
    message = await _persist_webhook_event(repository, event_data)

    return Message(message=message)


@router.get(
    "/",
    response_model=PaymentsPublic,
)
async def get_user_payments(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get authenticated user's payment history."""
    repository = PaymentRepository(session=session)
    payments, count = await repository.get_user_payments(
        user_email=current_user.email,
        skip=skip,
        limit=limit,
    )
    return PaymentsPublic(
        data=[PaymentPublic.model_validate(p.model_dump()) for p in payments],
        count=count,
    )


@router.get("/config", response_model=DonationConfigsPublic)
async def get_donation_configs(session: SessionDep) -> Any:
    """Get donation presets (public endpoint)."""
    statement = select(DonationConfig)
    result = await session.execute(statement)
    configs = list(result.scalars().all())
    return DonationConfigsPublic(
        data=[DonationConfigPublic.model_validate(c.model_dump()) for c in configs],
        count=len(configs),
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentPublic,
)
async def get_payment(
    payment_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Get a single payment detail."""
    repository = PaymentRepository(session=session)
    payment = await repository.get_by_id(payment_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.donor_email != current_user.email:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return PaymentPublic.model_validate(payment.model_dump())


# --------------------------------------------------------------------------- #
#  Module-level helpers                                                       #
# --------------------------------------------------------------------------- #


async def _check_amount_in_config(session: SessionDep, amount_cents: int) -> bool:
    """Check if amount matches a configured donation preset (or configs don't exist)."""
    result = await session.execute(select(DonationConfig))
    configs = list(result.scalars().all())
    if not configs:
        return True  # No configs means any amount is allowed
    return amount_cents in {c.amount_cents for c in configs}


def _log_payment_attempt(request: Request, amount_cents: int, donor_email: str | None) -> None:
    """Log a payment creation attempt."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    logger.info(
        "Payment attempt | amount=%d | donor_email=%s | ip=%s | ua=%s",
        amount_cents,
        donor_email or "guest",
        ip_address,
        user_agent[:200],
    )


async def _persist_webhook_event(repository: PaymentRepository, event_data: dict) -> str:
    """Persist a webhook event's side effects (delegate from route handler).

    Returns a user-facing message string for the route to include in its response.
    """
    event_type = event_data["type"]

    if event_type == "payment_intent.succeeded":
        existing = await repository.get_by_stripe_intent(event_data["payment_intent_id"])
        if existing:
            await repository.update_status(
                payment=existing,
                status=event_data["status"],
                receipt_url=event_data.get("receipt_url"),
            )
        else:
            await repository.create(
                {
                    "amount_cents": event_data["amount_cents"],
                    "currency": "usd",
                    "status": event_data["status"],
                    "stripe_payment_intent_id": event_data["payment_intent_id"],
                    "donor_email": event_data.get("donor_email"),
                    "donor_name": event_data.get("donor_name"),
                }
            )
        logger.info(
            "Webhook processed: payment_intent.succeeded | intent=%s",
            event_data["payment_intent_id"],
        )
        return "Payment succeeded"

    elif event_type == "payment_intent.payment_failed":
        existing = await repository.get_by_stripe_intent(event_data["payment_intent_id"])
        if existing:
            await repository.update_status(payment=existing, status=event_data["status"])
        logger.info(
            "Webhook processed: payment_intent.payment_failed | intent=%s",
            event_data["payment_intent_id"],
        )
        return "Payment failed"

    elif event_type == "checkout.session.completed":
        pi_id = event_data.get("payment_intent_id")
        if pi_id:
            existing = await repository.get_by_stripe_intent(pi_id)
            if existing:
                await repository.update_status(payment=existing, status="succeeded")
        logger.info(
            "Webhook processed: checkout.session.completed | session=%s",
            event_data.get("checkout_session_id"),
        )
        return "Checkout session completed"

    else:
        logger.warning("Webhook ignored: unknown event type %s", event_data.get("type"))
        return "Webhook event ignored"

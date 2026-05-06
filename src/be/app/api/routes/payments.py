from typing import Any

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
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()


@router.post(
    "/create-intent",
    response_model=PaymentIntentResponse,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[require_scope("payments:write")],
)
async def create_payment_intent_endpoint(
    payment_in: PaymentCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Create a Stripe PaymentIntent for a one-time donation."""
    result = await payment_service.create_payment_intent(
        amount_cents=payment_in.amount_cents,
        currency=payment_in.currency,
        donor_email=current_user.email if not payment_in.donor_email else payment_in.donor_email,
        donor_name=current_user.full_name if not payment_in.donor_name else payment_in.donor_name,
    )
    # Persist pending payment record
    repository = PaymentRepository(session=session)
    await repository.create(
        {
            "amount_cents": payment_in.amount_cents,
            "currency": payment_in.currency,
            "status": "pending",
            "stripe_payment_intent_id": result["payment_intent_id"],
            "donor_email": current_user.email,
            "donor_name": current_user.full_name,
        }
    )
    return PaymentIntentResponse(**result)


@router.post(
    "/create-subscription",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[require_scope("payments:write")],
)
async def create_subscription_endpoint(
    payment_in: PaymentCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Create a Stripe Checkout Session for a recurring donation."""
    result = await payment_service.create_checkout_session(
        amount_cents=payment_in.amount_cents,
        currency=payment_in.currency,
        donor_email=current_user.email if not payment_in.donor_email else payment_in.donor_email,
        donor_name=current_user.full_name if not payment_in.donor_name else payment_in.donor_name,
        recurring=True,
    )
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
            "donor_email": current_user.email,
            "donor_name": current_user.full_name,
        }
    )
    return CheckoutSessionResponse(**result)


@router.post("/webhook")
async def webhook_endpoint(request: Request, session: SessionDep) -> Message:
    """Handle Stripe webhook events."""
    body = await request.body()
    signature = request.headers.get("stripe-signature", "")
    # Bind session to service for credential resolution
    payment_service._session = session
    event_data = await payment_service.handle_webhook(session, body.decode(), signature)

    repository = PaymentRepository(session=session)

    if event_data["type"] == "payment_intent.succeeded":
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
        return Message(message="Payment succeeded")

    elif event_data["type"] == "payment_intent.payment_failed":
        existing = await repository.get_by_stripe_intent(event_data["payment_intent_id"])
        if existing:
            await repository.update_status(payment=existing, status=event_data["status"])
        return Message(message="Payment failed")

    elif event_data["type"] == "checkout.session.completed":
        pi_id = event_data.get("payment_intent_id")
        if pi_id:
            existing = await repository.get_by_stripe_intent(pi_id)
            if existing:
                await repository.update_status(payment=existing, status="succeeded")
        return Message(message="Checkout session completed")

    return Message(message="Webhook event ignored")


@router.get(
    "/",
    response_model=PaymentsPublic,
    # dependencies=[require_scope("payments:read")],
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
    # dependencies=[require_scope("payments:read")],
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

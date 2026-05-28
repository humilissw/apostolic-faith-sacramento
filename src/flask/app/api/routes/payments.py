from flask import Blueprint, jsonify, request

from app.api.deps import get_current_user, get_db
from app.models import DonationConfig
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

router = Blueprint("payments", __name__, url_prefix="/payments")
payment_service = PaymentService()


@router.route("/create-intent", methods=["POST"])
def create_payment_intent_endpoint():
    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    payment_in = PaymentCreate(**data)
    result = payment_service.create_payment_intent(
        amount_cents=payment_in.amount_cents,
        currency=payment_in.currency,
        donor_email=current_user.email if not payment_in.donor_email else payment_in.donor_email,
        donor_name=current_user.full_name if not payment_in.donor_name else payment_in.donor_name,
    )
    repository = PaymentRepository(session=session)
    repository.create(
        {
            "amount_cents": payment_in.amount_cents,
            "currency": payment_in.currency,
            "status": "pending",
            "stripe_payment_intent_id": result["payment_intent_id"],
            "donor_email": current_user.email,
            "donor_name": current_user.full_name,
        }
    )
    return jsonify(PaymentIntentResponse(**result).model_dump()), 201


@router.route("/create-subscription", methods=["POST"])
def create_subscription_endpoint():
    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    payment_in = PaymentCreate(**data)
    result = payment_service.create_checkout_session(
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
    repository.create(
        {
            "amount_cents": payment_in.amount_cents,
            "currency": payment_in.currency,
            "status": "pending",
            "stripe_payment_intent_id": checkout_session_id,
            "donor_email": current_user.email,
            "donor_name": current_user.full_name,
        }
    )
    return jsonify(CheckoutSessionResponse(**result).model_dump()), 201


@router.route("/webhook", methods=["POST"])
def webhook_endpoint():
    session = get_db()
    body = request.get_data().decode()
    signature = request.headers.get("stripe-signature", "")
    payment_service._session = session
    event_data = payment_service.handle_webhook(session, body, signature)
    repository = PaymentRepository(session=session)

    if event_data["type"] == "payment_intent.succeeded":
        existing = repository.get_by_stripe_intent(event_data["payment_intent_id"])
        if existing:
            repository.update_status(
                payment=existing,
                status=event_data["status"],
                receipt_url=event_data.get("receipt_url"),
            )
        else:
            repository.create(
                {
                    "amount_cents": event_data["amount_cents"],
                    "currency": "usd",
                    "status": event_data["status"],
                    "stripe_payment_intent_id": event_data["payment_intent_id"],
                    "donor_email": event_data.get("donor_email"),
                    "donor_name": event_data.get("donor_name"),
                }
            )
        return jsonify({"message": "Payment succeeded"})
    elif event_data["type"] == "payment_intent.payment_failed":
        existing = repository.get_by_stripe_intent(event_data["payment_intent_id"])
        if existing:
            repository.update_status(payment=existing, status=event_data["status"])
        return jsonify({"message": "Payment failed"})
    elif event_data["type"] == "checkout.session.completed":
        pi_id = event_data.get("payment_intent_id")
        if pi_id:
            existing = repository.get_by_stripe_intent(pi_id)
            if existing:
                repository.update_status(payment=existing, status="succeeded")
        return jsonify({"message": "Checkout session completed"})
    return jsonify({"message": "Webhook event ignored"})


@router.route("/", methods=["GET"])
def get_user_payments(skip: int = 0, limit: int = 100):
    session = get_db()
    current_user = get_current_user()
    repository = PaymentRepository(session=session)
    payments, count = repository.get_user_payments(
        user_email=current_user.email, skip=skip, limit=limit
    )
    return jsonify(
        PaymentsPublic(
            data=[PaymentPublic.model_validate(p.model_dump()) for p in payments], count=count
        ).model_dump()
    )


@router.route("/config", methods=["GET"])
def get_donation_configs():
    session = get_db()
    from sqlalchemy import select

    statement = select(DonationConfig)
    result = session.execute(statement)
    configs = list(result.scalars().all())
    return jsonify(
        DonationConfigsPublic(
            data=[DonationConfigPublic.model_validate(c.model_dump()) for c in configs],
            count=len(configs),
        ).model_dump()
    )


@router.route("/<payment_id>", methods=["GET"])
def get_payment(payment_id: str):
    session = get_db()
    current_user = get_current_user()
    repository = PaymentRepository(session=session)
    payment = repository.get_by_id(payment_id=payment_id)
    if not payment:
        return jsonify({"detail": "Payment not found"}), 404
    if payment.donor_email != current_user.email:
        return jsonify({"detail": "Not enough permissions"}), 403
    return jsonify(PaymentPublic.model_validate(payment.model_dump()))

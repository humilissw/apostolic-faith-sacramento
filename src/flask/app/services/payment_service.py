import json
from typing import Any

import stripe
from flask import HTTPException

from app.config import settings


class PaymentService:
    _session: Any | None = None

    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def _resolve_stripe_key(self) -> str:
        from app.models import IntegrationConfig
        from sqlalchemy import select

        assert (
            self._session is not None
        ), "PaymentService requires a session for credential resolution"
        stripe_filter = IntegrationConfig.type == "stripe"
        stmt = select(IntegrationConfig).where(stripe_filter)
        result = self._session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration and integration.enabled and integration.cred_encrypted_blob:
            from app.services.integration_service import EncryptionHelper

            plaintext = EncryptionHelper.decrypt(
                integration.cred_encrypted_iv, integration.cred_encrypted_blob
            )
            creds: dict[str, str] = json.loads(plaintext)
            if creds.get("secret_key"):
                return creds["secret_key"]

        if settings.STRIPE_SECRET_KEY:
            return settings.STRIPE_SECRET_KEY
        raise HTTPException(500, "Stripe is not configured")

    def _resolve_webhook_secret(self) -> str:
        from app.models import IntegrationConfig
        from sqlalchemy import select

        assert (
            self._session is not None
        ), "PaymentService requires a session for credential resolution"
        stripe_filter = IntegrationConfig.type == "stripe"
        stmt = select(IntegrationConfig).where(stripe_filter)
        result = self._session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration and integration.enabled and integration.cred_encrypted_blob:
            from app.services.integration_service import EncryptionHelper

            plaintext = EncryptionHelper.decrypt(
                integration.cred_encrypted_iv, integration.cred_encrypted_blob
            )
            creds: dict[str, str] = json.loads(plaintext)
            if creds.get("webhook_secret"):
                return creds["webhook_secret"]

        if settings.STRIPE_WEBHOOK_SECRET:
            return settings.STRIPE_WEBHOOK_SECRET
        raise HTTPException(500, "Stripe webhook secret is not configured")

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        donor_email: str | None = None,
        donor_name: str | None = None,
    ) -> dict[str, str]:
        if self._session is None:
            raise HTTPException(500, "PaymentService requires a session for credential resolution")
        secret_key = self._resolve_stripe_key()
        stripe.api_key = secret_key
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={"donor_email": donor_email or "", "donor_name": donor_name or ""},
            )
            return {"client_secret": intent.client_secret, "payment_intent_id": intent.id}
        except stripe.error.StripeError as e:
            raise HTTPException(400, detail=f"Stripe error: {str(e)}")

    def create_checkout_session(
        self,
        amount_cents: int,
        currency: str,
        donor_email: str | None = None,
        donor_name: str | None = None,
        recurring: bool = False,
    ) -> dict[str, Any]:
        if self._session is None:
            raise HTTPException(500, "PaymentService requires a session for credential resolution")
        secret_key = self._resolve_stripe_key()
        stripe.api_key = secret_key
        try:
            line_items = [
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {"name": "Apostolic Faith Sacramento Donation"},
                        "unit_amount": amount_cents,
                        "recurring": {"interval": "month"} if recurring else None,
                    },
                    "quantity": 1,
                }
            ]
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="subscription" if recurring else "payment",
                customer_email=donor_email,
                metadata={"donor_email": donor_email or "", "donor_name": donor_name or ""},
                success_url=f"{settings.FRONTEND_HOST}/donate/?status=success",
                cancel_url=f"{settings.FRONTEND_HOST}/donate/?status=cancelled",
            )
            return {
                "client_secret": session.client_secret if hasattr(session, "client_secret") else "",
                "type": "checkout",
                "checkout_url": session.url,
            }
        except stripe.error.StripeError as e:
            raise HTTPException(400, detail=f"Stripe error: {str(e)}")

    def handle_webhook(self, session: Any, body: str, signature: str) -> dict[str, Any]:
        webhook_secret = self._resolve_webhook_secret_for_session(session)
        try:
            event = stripe.Webhook.construct_event(body, signature, webhook_secret)
        except ValueError:
            raise HTTPException(400, detail="Invalid webhook payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(400, detail="Invalid webhook signature")

        if event["type"] == "payment_intent.succeeded":
            pi = event["data"]["object"]
            return {
                "type": "payment_intent.succeeded",
                "payment_intent_id": pi["id"],
                "amount_cents": pi["amount"],
                "status": "succeeded",
                "receipt_url": pi.get("receipt_url"),
                "donor_email": pi.get("metadata", {}).get("donor_email"),
                "donor_name": pi.get("metadata", {}).get("donor_name"),
            }
        elif event["type"] == "payment_intent.payment_failed":
            pi = event["data"]["object"]
            return {
                "type": "payment_intent.payment_failed",
                "payment_intent_id": pi["id"],
                "status": "failed",
            }
        elif event["type"] == "checkout.session.completed":
            session_obj = event["data"]["object"]
            return {
                "type": "checkout.session.completed",
                "checkout_session_id": session_obj["id"],
                "payment_intent_id": session_obj.get("payment_intent"),
                "status": "succeeded",
                "donor_email": session_obj.get("customer_email"),
            }
        elif event["type"] == "checkout.session.expired":
            session_obj = event["data"]["object"]
            return {
                "type": "checkout.session.expired",
                "checkout_session_id": session_obj["id"],
                "status": "expired",
            }

        return {"type": "unknown", "status": "ignored"}

    def _resolve_webhook_secret_for_session(self, session: Any) -> str:
        from app.models import IntegrationConfig
        from sqlalchemy import select

        stripe_filter = IntegrationConfig.type == "stripe"
        stmt = select(IntegrationConfig).where(stripe_filter)
        result = session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration and integration.enabled and integration.cred_encrypted_blob:
            from app.services.integration_service import EncryptionHelper

            plaintext = EncryptionHelper.decrypt(
                integration.cred_encrypted_iv, integration.cred_encrypted_blob
            )
            creds: dict[str, str] = json.loads(plaintext)
            if creds.get("webhook_secret"):
                return creds["webhook_secret"]

        if settings.STRIPE_WEBHOOK_SECRET:
            return settings.STRIPE_WEBHOOK_SECRET
        raise HTTPException(500, "Stripe webhook secret is not configured")

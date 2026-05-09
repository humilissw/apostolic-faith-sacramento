import json
from typing import Any

import stripe
from fastapi import HTTPException

from app.config import settings


class PaymentService:
    # session used for credential resolution (set by route handler)
    _session: Any | None = None

    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def _resolve_stripe_key(self) -> str:
        """Resolve Stripe secret key from DB config or env var fallback."""
        from app.models import IntegrationConfig
        from sqlalchemy import select

        assert (
            self._session is not None
        ), "PaymentService requires a session for credential resolution"

        # Try DB config first
        stripe_filter = IntegrationConfig.type == "stripe"  # type: ignore[arg-type]
        stmt = select(IntegrationConfig).where(stripe_filter)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration and integration.enabled and integration.cred_encrypted_blob:
            from app.services.integration_service import EncryptionHelper

            plaintext = EncryptionHelper.decrypt(
                integration.cred_encrypted_iv,
                integration.cred_encrypted_blob,
            )
            creds: dict[str, str] = json.loads(plaintext)  # type: ignore[assignment]
            if creds.get("secret_key"):
                return creds["secret_key"]

        # Fallback to env var
        if settings.STRIPE_SECRET_KEY:
            return settings.STRIPE_SECRET_KEY
        raise HTTPException(500, "Stripe is not configured")

    async def _resolve_webhook_secret(self) -> str:
        """Resolve Stripe webhook secret from DB config or env var fallback."""
        from app.models import IntegrationConfig
        from sqlalchemy import select

        assert (
            self._session is not None
        ), "PaymentService requires a session for credential resolution"

        stripe_filter = IntegrationConfig.type == "stripe"  # type: ignore[arg-type]
        stmt = select(IntegrationConfig).where(stripe_filter)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration and integration.enabled and integration.cred_encrypted_blob:
            from app.services.integration_service import EncryptionHelper

            plaintext = EncryptionHelper.decrypt(
                integration.cred_encrypted_iv,
                integration.cred_encrypted_blob,
            )
            creds: dict[str, str] = json.loads(plaintext)  # type: ignore[assignment]
            if creds.get("webhook_secret"):
                return creds["webhook_secret"]

        if settings.STRIPE_WEBHOOK_SECRET:
            return settings.STRIPE_WEBHOOK_SECRET
        raise HTTPException(500, "Stripe webhook secret is not configured")

    async def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        donor_email: str | None = None,
        donor_name: str | None = None,
    ) -> dict[str, str]:
        """Create a Stripe PaymentIntent for a one-time donation."""
        if self._session is None:
            raise HTTPException(500, "PaymentService requires a session for credential resolution")

        secret_key = await self._resolve_stripe_key()
        stripe.api_key = secret_key

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    "donor_email": donor_email or "",
                    "donor_name": donor_name or "",
                },
            )
            return {
                "client_secret": intent.client_secret,  # type: ignore[dict-item]
                "payment_intent_id": intent.id,
            }
        except stripe.error.StripeError as e:  # type: ignore[attr-defined]
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    async def create_checkout_session(
        self,
        amount_cents: int,
        currency: str,
        donor_email: str | None = None,
        donor_name: str | None = None,
        recurring: bool = False,
    ) -> dict[str, Any]:
        """Create a Stripe Checkout Session for one-time or recurring payments."""
        if self._session is None:
            raise HTTPException(500, "PaymentService requires a session for credential resolution")

        secret_key = await self._resolve_stripe_key()
        stripe.api_key = secret_key

        try:
            line_items = [
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": "Apostolic Faith Sacramento Donation",
                        },
                        "unit_amount": amount_cents,
                        "recurring": {"interval": "month"} if recurring else None,
                    },
                    "quantity": 1,
                }
            ]

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,  # type: ignore[arg-type]
                mode="subscription" if recurring else "payment",
                customer_email=donor_email,  # type: ignore[arg-type]
                metadata={
                    "donor_email": donor_email or "",
                    "donor_name": donor_name or "",
                },
                success_url=f"{settings.FRONTEND_HOST}/donate/?status=success",
                cancel_url=f"{settings.FRONTEND_HOST}/donate/?status=cancelled",
            )
            return {
                "client_secret": session.client_secret if hasattr(session, "client_secret") else "",
                "type": "checkout",
                "checkout_url": session.url,
            }
        except stripe.error.StripeError as e:  # type: ignore[attr-defined]
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    async def handle_webhook(self, session: Any, body: str, signature: str) -> dict[str, Any]:
        """Verify webhook signature and return event data for the route to process."""
        webhook_secret = await self._resolve_webhook_secret_for_session(session)
        try:
            event = stripe.Webhook.construct_event(body, signature, webhook_secret)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        except stripe.error.SignatureVerificationError:  # type: ignore[attr-defined]
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

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

    async def _resolve_webhook_secret_for_session(self, session: Any) -> str:
        """Resolve webhook secret using a SQLModel session."""
        from app.models import IntegrationConfig
        from sqlalchemy import select

        stripe_filter = IntegrationConfig.type == "stripe"  # type: ignore[arg-type]
        stmt = select(IntegrationConfig).where(stripe_filter)  # type: ignore[arg-type]
        result = await session.execute(stmt)
        integration = result.scalar_one_or_none()

        if integration and integration.enabled and integration.cred_encrypted_blob:
            from app.services.integration_service import EncryptionHelper

            plaintext = EncryptionHelper.decrypt(
                integration.cred_encrypted_iv,
                integration.cred_encrypted_blob,
            )
            creds: dict[str, str] = json.loads(plaintext)  # type: ignore[assignment]
            if creds.get("webhook_secret"):
                return creds["webhook_secret"]

        if settings.STRIPE_WEBHOOK_SECRET:
            return settings.STRIPE_WEBHOOK_SECRET
        raise HTTPException(500, "Stripe webhook secret is not configured")

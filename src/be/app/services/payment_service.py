"""
Payment service for handling Stripe payment operations.

Handles:
- PaymentIntent creation (one-time donations)
- Checkout session creation (recurring donations)
- Webhook event verification and routing
- Credential resolution from DB config or env vars
"""

import json
from typing import Any

import stripe
from fastapi import HTTPException, Request

from app.config import settings


class PaymentService:
    """Stripe payment service with credential resolution."""

    _session: Any | None = None  # Set by route handler for credential resolution

    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def _resolve_stripe_key(self) -> str:
        """Resolve Stripe secret key from DB config or env var fallback."""
        from app.models import IntegrationConfig
        from sqlalchemy import select

        # Try DB config first
        stripe_filter = IntegrationConfig.type == "stripe"  # type: ignore[arg-type]
        stmt = select(IntegrationConfig).where(stripe_filter)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)  # type: ignore[union-attr]
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

        stripe_filter = IntegrationConfig.type == "stripe"  # type: ignore[arg-type]
        stmt = select(IntegrationConfig).where(stripe_filter)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)  # type: ignore[union-attr]
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

    async def handle_webhook(self, body: str, signature: str) -> dict[str, Any]:
        """Verify webhook signature and route to the appropriate handler.

        Returns event data dict for the route to persist.
        """
        try:
            event = stripe.Webhook.construct_event(
                body, signature, await self._resolve_webhook_secret()
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        except stripe.error.SignatureVerificationError:  # type: ignore[attr-defined]
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        return self._route_webhook_event(event)

    def _route_webhook_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Route a verified Stripe webhook event to the appropriate handler."""
        event_type = event["type"]
        data_obj = event.get("data", {}).get("object", {})

        if event_type == "payment_intent.succeeded":
            return {
                "type": "payment_intent.succeeded",
                "payment_intent_id": data_obj["id"],
                "amount_cents": data_obj["amount"],
                "status": "succeeded",
                "receipt_url": data_obj.get("receipt_url"),
                "donor_email": data_obj.get("metadata", {}).get("donor_email"),
                "donor_name": data_obj.get("metadata", {}).get("donor_name"),
            }
        elif event_type == "payment_intent.payment_failed":
            return {
                "type": "payment_intent.payment_failed",
                "payment_intent_id": data_obj["id"],
                "status": "failed",
            }
        elif event_type == "checkout.session.completed":
            return {
                "type": "checkout.session.completed",
                "checkout_session_id": data_obj["id"],
                "payment_intent_id": data_obj.get("payment_intent"),
                "status": "succeeded",
                "donor_email": data_obj.get("customer_email"),
            }
        elif event_type == "checkout.session.expired":
            return {
                "type": "checkout.session.expired",
                "checkout_session_id": data_obj["id"],
                "status": "expired",
            }

        return {"type": "unknown", "status": "ignored"}


# --------------------------------------------------------------------------- #
#  Shared helpers for route handlers                                          #
# --------------------------------------------------------------------------- #


async def extract_donor_info_from_request(request: Request) -> tuple[str | None, str | None]:
    """Extract donor email/name from an authenticated request.

    Tries cookie token first, then Authorization header.
    Returns (email, full_name) — both may be None for guest requests.
    """
    import jwt as _jwt
    from jwt.exceptions import InvalidTokenError as _InvalidTokenError

    from app.api.deps import get_token_from_cookie
    from app.core import security

    token_to_use: str | None = None

    cookie_token = await get_token_from_cookie(request)
    if cookie_token:
        token_to_use = cookie_token

    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token_to_use = auth_header[7:]

    if not token_to_use:
        return None, None

    try:
        decode_kwargs: dict = {}
        if settings.JWT_AUDIENCE:
            decode_kwargs["audience"] = settings.JWT_AUDIENCE
        if settings.JWT_ISSUER:
            decode_kwargs["issuer"] = settings.JWT_ISSUER
        payload = _jwt.decode(
            token_to_use,
            security.PUBLIC_KEY,
            algorithms=[security.ALGORITHM],
            **decode_kwargs,
        )
        return payload.get("sub"), None  # sub is email; name not in JWT
    except _InvalidTokenError:
        return None, None
    except Exception:
        return None, None

from pydantic import BaseModel
from datetime import datetime


class PaymentPublic(BaseModel):
    id: str
    amount_cents: int
    currency: str
    status: str
    stripe_payment_intent_id: str
    stripe_subscription_id: str | None
    donor_email: str | None
    donor_name: str | None
    receipt_url: str | None
    created_on: datetime
    updated_on: datetime | None


class PaymentsPublic(BaseModel):
    data: list[PaymentPublic]
    count: int


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str


class CheckoutSessionResponse(BaseModel):
    client_secret: str
    type: str = "checkout"
    checkout_url: str


class DonationConfigPublic(BaseModel):
    id: str
    label: str
    amount_cents: int
    is_default: bool
    frequency: str
    created_on: datetime
    updated_on: datetime | None


class DonationConfigsPublic(BaseModel):
    data: list[DonationConfigPublic]
    count: int

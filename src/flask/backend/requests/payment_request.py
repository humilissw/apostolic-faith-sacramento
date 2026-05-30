from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    amount_cents: int = Field(..., gt=0, le=999999999)
    currency: str = Field(default="usd", max_length=3)
    frequency: str = Field(..., pattern="^(one_time|recurring)$")
    donor_email: str | None = Field(default=None, max_length=255)
    donor_name: str | None = Field(default=None, max_length=255)
    metadata_json: str | None = Field(default=None, max_length=4000)

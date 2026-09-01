from pydantic import BaseModel, Field, field_validator


class PaymentCreate(BaseModel):
    amount_cents: int = Field(..., gt=0, le=999999999)
    currency: str = Field(default="usd", max_length=3)
    frequency: str = Field(..., pattern="^(one_time|recurring)$")
    donor_email: str | None = Field(default=None, max_length=254)
    donor_name: str | None = Field(default=None, max_length=100)
    metadata_json: str | None = Field(default=None, max_length=4000)

    @field_validator("donor_email")
    @classmethod
    def validate_donor_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Basic email format validation (RFC 5322 simplified)
        import re

        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid donor email format")
        return v

from werkzeug.exceptions import HTTPException
from sqlalchemy import select

from backend.models import Payment


class PaymentRepository:
    def __init__(self, session):
        self.session = session

    def create(self, payment_in: dict) -> Payment:
        try:
            payment = Payment(**payment_in)
            self.session.add(payment)
            self.session.commit()
            self.session.refresh(payment)
            return payment
        except Exception:
            self.session.rollback()
            raise HTTPException(500, detail="Database error while creating payment")

    def get_by_id(self, payment_id: str) -> Payment | None:
        statement = select(Payment).where(Payment.id == payment_id)
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_by_stripe_intent(self, stripe_intent_id: str) -> Payment | None:
        statement = select(Payment).where(Payment.stripe_payment_intent_id == stripe_intent_id)
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Payment], int]:
        count_statement = select(Payment)
        count_result = self.session.execute(count_statement)
        total_count = len(count_result.scalars().all())
        statement = select(Payment).offset(skip).limit(limit)
        result = self.session.execute(statement)
        return list(result.scalars().all()), total_count or 0

    def get_user_payments(self, user_email: str, skip: int = 0, limit: int = 100) -> tuple[list[Payment], int]:
        count_statement = select(Payment).where(Payment.donor_email == user_email)
        count_result = self.session.execute(count_statement)
        total_count = len(count_result.scalars().all())
        statement = select(Payment).where(Payment.donor_email == user_email).offset(skip).limit(limit)
        result = self.session.execute(statement)
        return list(result.scalars().all()), total_count or 0

    def update_status(self, payment: Payment, status: str, receipt_url: str | None = None) -> Payment:
        payment.status = status
        if receipt_url:
            payment.receipt_url = receipt_url
        payment.updated_on = payment.updated_on or payment.created_on
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def update_with_metadata(self, payment: Payment, metadata_json: str) -> Payment:
        payment.metadata_json = metadata_json
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

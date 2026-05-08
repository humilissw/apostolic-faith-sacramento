from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payment_in: dict) -> Payment:
        try:
            payment = Payment(**payment_in)
            self.session.add(payment)
            await self.session.commit()
            await self.session.refresh(payment)
            return payment
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Database error while creating payment")

    async def get_by_id(self, payment_id: str) -> Payment | None:
        statement = select(Payment).where(Payment.id == payment_id)  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_stripe_intent(self, stripe_intent_id: str) -> Payment | None:
        statement = select(Payment).where(
            Payment.stripe_payment_intent_id == stripe_intent_id  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Payment], int]:
        count_statement = select(Payment)
        count_result = await self.session.execute(count_statement)
        total_count = len(count_result.scalars().all())

        statement = select(Payment).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all()), total_count or 0

    async def get_user_payments(
        self, user_email: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Payment], int]:
        count_statement = select(Payment).where(
            Payment.donor_email == user_email  # type: ignore[arg-type]
        )
        count_result = await self.session.execute(count_statement)
        total_count = len(count_result.scalars().all())

        statement = (
            select(Payment)
            .where(Payment.donor_email == user_email)  # type: ignore[arg-type]
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all()), total_count or 0

    async def update_status(
        self, payment: Payment, status: str, receipt_url: str | None = None
    ) -> Payment:
        payment.status = status
        if receipt_url:
            payment.receipt_url = receipt_url
        payment.updated_on = payment.updated_on or payment.created_on
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def update_with_metadata(self, payment: Payment, metadata_json: str) -> Payment:
        payment.metadata_json = metadata_json
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

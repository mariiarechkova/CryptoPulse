from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.enums import PaymentProvider, PaymentStatus
from app.billing.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_pending(
        self,
        *,
        user_id: int,
        tariff_plan_id: int,
        amount,
        asset: str,
    ) -> Payment:
        payment = Payment(
            user_id=user_id,
            provider=PaymentProvider.CRYPTOBOT,
            status=PaymentStatus.PENDING,
            tariff_plan_id=tariff_plan_id,
            amount=amount,
            asset=asset,
            invoice_id="TEMP",
        )
        self._session.add(payment)
        await self._session.flush()

        # invoice_id unique+not null
        payment.invoice_id = f"TEMP-{payment.id}"
        await self._session.flush()

        return payment

    async def get_by_id(self, payment_id: int) -> Payment | None:
        res = await self._session.execute(select(Payment).where(Payment.id == payment_id))
        return res.scalar_one_or_none()

    async def get_by_invoice_id(self, invoice_id: str) -> Payment | None:
        res = await self._session.execute(select(Payment).where(Payment.invoice_id == invoice_id))
        return res.scalar_one_or_none()

    async def mark_paid(
        self,
        payment: Payment,
        *,
        paid_at: datetime,
        raw_payload: str | None = None,
    ) -> None:
        payment.status = PaymentStatus.PAID
        payment.paid_at = paid_at

        if raw_payload is not None:
            payment.raw_payload = raw_payload

        await self._session.flush()

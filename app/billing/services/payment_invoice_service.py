import json
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.enums import TariffCode
from app.billing.repositories.payment_repository import PaymentRepository
from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository
from infrastructure.cryptobot.cryptopay_client import CryptoPayClient


@dataclass(frozen=True)
class CreateInvoiceResult:
    payment_id: int
    invoice_id: str
    pay_url: str


class PaymentInvoiceService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        user_repo: UserRepository,
        tariff_repo: TariffPlanRepository,
        payment_repo: PaymentRepository,
        cryptopay: CryptoPayClient,
    ) -> None:
        self._session = session
        self._user_repo = user_repo
        self._tariff_repo = tariff_repo
        self._payment_repo = payment_repo
        self._cryptopay = cryptopay

    async def create_invoice(self, *, telegram_id: int, tariff_code: TariffCode) -> CreateInvoiceResult:
        plan = await self._tariff_repo.get_by_code(tariff_code.value)
        if not plan:
            raise ValueError("Tariff plan not found or inactive")

        user = await self._user_repo.get_by_telegram_id(telegram_id)
        if not user:
            free_plan = await self._tariff_repo.get_by_code(TariffCode.FREE.value)
            if not free_plan:
                raise ValueError("Free tariff plan not found or inactive")
            user = await self._user_repo.create(telegram_id=telegram_id, tariff_plan_id=free_plan.id)

        payment = await self._payment_repo.create_pending(
            user_id=user.id,
            tariff_plan_id=plan.id,
            amount=Decimal(str(plan.price_amount)),
            asset=plan.price_currency,
        )

        invoice = await self._cryptopay.create_invoice(
            amount=str(payment.amount),
            asset=payment.asset,
            description=f"CryptoPulse: {plan.title}",
            payload=str(payment.id),
            expires_in=60 * 30,
        )

        payment.invoice_id = invoice.invoice_id
        payment.raw_payload = json.dumps({"pay_url": invoice.pay_url, "invoice": invoice.raw}, ensure_ascii=False)

        await self._session.commit()

        return CreateInvoiceResult(payment_id=payment.id, invoice_id=invoice.invoice_id, pay_url=invoice.pay_url)
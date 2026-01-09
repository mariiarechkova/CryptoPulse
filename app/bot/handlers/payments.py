import inspect
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.billing.enums import TariffCode
from app.billing.repositories.payment_repository import PaymentRepository
from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository
from app.billing.services.payment_invoice_service import PaymentInvoiceService
from infrastructure.cryptobot.cryptopay_client import CryptoPayClient
from infrastructure.db.session import async_session_maker

router = Router()

cryptopay = CryptoPayClient(api_token=os.environ["CRYPTOBOT_API_TOKEN"])


@router.callback_query(F.data == "buy_subscription")
async def buy_subscription_callback(callback: CallbackQuery):
    await callback.answer()

    async with async_session_maker() as session:
        service = PaymentInvoiceService(
            session=session,
            user_repo=UserRepository(session),
            tariff_repo=TariffPlanRepository(session),
            payment_repo=PaymentRepository(session),
            cryptopay=cryptopay,
        )

        res = await service.create_invoice(
            telegram_id=callback.from_user.id,
            tariff_code=TariffCode.PAID_MONTH,
        )

    await callback.message.answer(f"💳 Оплати подписку по ссылке:\n{res.pay_url}")
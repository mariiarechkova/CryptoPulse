from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.enums import PaymentStatus
from app.billing.repositories.payment_repository import PaymentRepository
from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WebhookHandleResult:
    action: str
    invoice_id: str | None = None
    payment_id: int | None = None
    user_id: int | None = None


class PaymentWebhookService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        payment_repo: PaymentRepository,
        user_repo: UserRepository,
        tariff_repo: TariffPlanRepository,
    ) -> None:
        self._session = session
        self._payment_repo = payment_repo
        self._user_repo = user_repo
        self._tariff_repo = tariff_repo

    async def handle_update(self, *, update: dict[str, Any]) -> WebhookHandleResult:
        update_type = update.get("update_type")
        logger.info("CryptoPay webhook received", extra={"update_type": update_type})

        if update_type != "invoice_paid":
            return WebhookHandleResult(action="ignored")

        payload = self._extract_payload(update)
        if payload is None:
            return WebhookHandleResult(action="bad_payload")

        invoice_id = self._extract_invoice_id(payload)
        if invoice_id is None:
            logger.warning("CryptoPay webhook without invoice_id")
            return WebhookHandleResult(action="bad_payload")

        payment = await self._payment_repo.get_by_invoice_id(invoice_id)
        if payment is None:
            logger.warning("CryptoPay invoice not found", extra={"invoice_id": invoice_id})
            return WebhookHandleResult(action="not_found", invoice_id=invoice_id)

        if payment.status == PaymentStatus.PAID:
            logger.info(
                "CryptoPay invoice already paid (idempotent)",
                extra={"invoice_id": invoice_id, "payment_id": payment.id},
            )
            return WebhookHandleResult(
                action="ignored",
                invoice_id=invoice_id,
                payment_id=payment.id,
                user_id=payment.user_id,
            )

        paid_at = datetime.now(UTC)
        raw_payload = json.dumps(update, ensure_ascii=False)

        await self._payment_repo.mark_paid(payment, paid_at=paid_at, raw_payload=raw_payload)

        await self._apply_payment_to_user(payment=payment)

        await self._session.commit()

        logger.info(
            "CryptoPay payment applied",
            extra={
                "invoice_id": invoice_id,
                "payment_id": payment.id,
                "user_id": payment.user_id,
                "tariff_plan_id": payment.tariff_plan_id,
            },
        )

        return WebhookHandleResult(
            action="paid",
            invoice_id=invoice_id,
            payment_id=payment.id,
            user_id=payment.user_id,
        )

    def _extract_payload(self, update: dict[str, Any]) -> dict[str, Any] | None:
        payload = update.get("payload")
        if not isinstance(payload, dict):
            logger.warning("CryptoPay webhook: payload is not a dict")
            return None
        return payload

    def _extract_invoice_id(self, payload: dict[str, Any]) -> str | None:
        invoice = payload.get("invoice")

        if isinstance(invoice, dict):
            inv_id = invoice.get("invoice_id")
            if inv_id is not None:
                return str(inv_id)

        inv_id_raw = payload.get("invoice_id")
        return str(inv_id_raw) if inv_id_raw is not None else None

    async def _apply_payment_to_user(self, *, payment) -> None:
        user = await self._user_repo.get_by_id(payment.user_id)
        if user is None:
            return

        user.tariff_plan_id = payment.tariff_plan_id

        plan = await self._tariff_repo.get_by_id(payment.tariff_plan_id)
        if plan is None:
            logger.warning("TariffPlan not found", extra={"tariff_plan_id": payment.tariff_plan_id})
            await self._session.flush()
            return

        now = datetime.now(UTC)
        base = user.paid_until if user.paid_until and user.paid_until > now else now

        user.paid_until = self._calc_paid_until(base=base, plan_code=plan.code)

        await self._session.flush()

    def _calc_paid_until(self, *, base: datetime, plan_code: str) -> datetime:
        if plan_code == "paid_month":
            return base + relativedelta(months=1)
        if plan_code == "paid_year":
            return base + relativedelta(years=1)
        return base + relativedelta(months=1)

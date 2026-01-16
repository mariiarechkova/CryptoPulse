import logging
from datetime import UTC, datetime
from typing import List

from app.alerts.models import Alert
from app.alerts.repository import AlertRepository
from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class ActiveSymbolLimitError(Exception):
    pass


class AlertService:
    def __init__(self, alert_repo: AlertRepository, session_factory):
        self._repo = alert_repo
        self._session_factory = session_factory

    async def get_user_alerts(self, user_id: int):
        return await self._repo.get_all(user_id)

    async def list_active_symbols(self) -> List[str]:
        return await self._repo.get_active_symbols()

    async def create(self, *, telegram_id: int, symbol: str, price: float, direction: str) -> Alert:
        async with self._session_factory() as session:
            user_repo = UserRepository(session)
            tariff_repo = TariffPlanRepository(session)

            free_plan = await tariff_repo.get_by_code("free")
            if free_plan is None:
                raise RuntimeError("TariffPlan with code='free' not found")

            user = await user_repo.get_by_telegram_id(telegram_id)
            if user is None:
                user = await user_repo.create(
                    telegram_id=telegram_id,
                    tariff_plan_id=free_plan.id,
                )

            now = datetime.now(UTC)
            is_paid = user.paid_until is not None and user.paid_until > now

            if is_paid:
                plan = await tariff_repo.get_by_id(user.tariff_plan_id)
            else:
                plan = free_plan

            if plan is None:
                raise RuntimeError("Tariff plan not found")

            active_symbols = await self._repo.get_active_symbols_in_session(
                session, user.telegram_id
            )
            if symbol not in active_symbols and len(active_symbols) >= plan.max_symbols:
                raise ActiveSymbolLimitError()

            alert = await self._repo.create(
                session,
                symbol=symbol,
                target_price=price,
                user_id=user.telegram_id,
                direction=direction,
            )

            await session.commit()
            return alert

    async def deactivate_alert(self, alert_id, user_id) -> tuple[bool, str | None]:
        alert = await self._repo.get_by_id_and_user(alert_id, user_id)
        if alert is None:
            return False, None

        symbol = alert.symbol
        updated = await self._repo.deactivate(alert.id)
        if not updated:
            return False, None

        return True, symbol

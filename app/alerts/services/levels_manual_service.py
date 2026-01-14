from datetime import UTC, datetime

from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository


class LevelsDemoLimitError(Exception):
    """Free user has no demo attempts left."""


class LevelsManualService:
    def __init__(self, *, session_factory, text_builder) -> None:
        self._session_factory = session_factory
        self._builder = text_builder  # LevelsTextBuilder

    async def build_text(self, *, telegram_id: int, symbol: str) -> str:
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

            is_paid = user.paid_until is not None and user.paid_until > datetime.now(UTC)

            if is_paid:
                return await self._builder.build_for_symbol(symbol=symbol)

            if user.levels_demo_remaining <= 0:
                raise LevelsDemoLimitError()

            text = await self._builder.build_for_symbol(symbol=symbol)

            res = await user_repo.try_consume_levels_demo(user.id)
            if not res:
                raise LevelsDemoLimitError()

            await session.commit()
            return text

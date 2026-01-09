from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.enums import TariffCode
from app.billing.models.tariff_plan import TariffPlan


class TariffPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_by_code(self, code: str) -> TariffPlan | None:
        res = await self._session.execute(
            select(TariffPlan).where(
                TariffPlan.code == code,
                TariffPlan.is_active.is_(True),
            )
        )
        return res.scalar_one_or_none()
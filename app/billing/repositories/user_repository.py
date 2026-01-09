from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        res = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return res.scalar_one_or_none()

    async def create(self, *, telegram_id: int, tariff_plan_id: int) -> User:
        user = User(telegram_id=telegram_id, tariff_plan_id=tariff_plan_id)
        self._session.add(user)
        await self._session.flush()
        return user
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        res = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return res.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        res = await self._session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def create(self, *, telegram_id: int, tariff_plan_id: int) -> User:
        user = User(telegram_id=telegram_id, tariff_plan_id=tariff_plan_id)
        self._session.add(user)
        await self._session.flush()
        return user

    async def try_consume_levels_demo(self, user_id: int) -> bool:
        result = await self._session.execute(
            update(User)
            .where(User.id == user_id, User.levels_demo_remaining > 0)
            .values(levels_demo_remaining=User.levels_demo_remaining - 1)
            .returning(User.id)
        )
        return result.scalar_one_or_none() is not None
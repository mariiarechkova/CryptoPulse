from typing import Optional

from sqlalchemy import select, update
from app.alerts.models import Alert


class AlertRepository:
    def __init__(self, session_factory):
        self._session_factory = session_factory


    async def create(self, symbol: str, target_price: float, user_id: int, direction:Optional[str] ) -> Alert:
        async with self._session_factory() as session:
            alert = Alert(
                symbol=symbol,
                target_price=target_price,
                user_id=user_id,
                direction=direction,
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert

    async def get_all(self, user_id: int) -> list[Alert]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Alert)
                .where(Alert.user_id == user_id, Alert.is_active.is_(True))
                .order_by(Alert.created_at.desc())
            )
            return result.scalars().all()

    async def get_active_for_symbol(self, symbol: str) -> list[Alert]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Alert)
                .where(Alert.symbol == symbol, Alert.is_active.is_(True))
                .order_by(Alert.created_at.desc())
            )
            return result.scalars().all()

    async def get_all_active(self) -> list[Alert]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Alert)
                .where(Alert.is_active.is_(True))
                .order_by(Alert.created_at.desc())
            )
            return result.scalars().all()

    async def get_by_id_and_user(self, alert_id: int, user_id: int):
        async with self._session_factory() as session:
            stmt = (
                select(Alert)
                .where(
                    Alert.id == alert_id,
                    Alert.user_id == user_id,
                    Alert.is_active.is_(True),
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def deactivate(self, alert_id: int) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                update(Alert)
                .where(Alert.id == alert_id)
                .values(is_active=False)
            )
            await session.commit()
            return result.rowcount > 0
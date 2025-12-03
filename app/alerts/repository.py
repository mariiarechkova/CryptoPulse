from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.alerts.models import Alert


class AlertRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, symbol: str, target_price: float, user_id: int, direction:Optional[str] ) -> Alert:
        alert = Alert(symbol=symbol, target_price=target_price, user_id=user_id, direction=direction)
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert


    async def get_all(self, user_id: int) -> list[Alert]:
        result = await self.session.execute(
            select(Alert).where(Alert.user_id == user_id, Alert.is_active.is_(True)).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def get_active_for_symbol(self, symbol: str) -> list[Alert]:
        result = await self.session.execute(
            select(Alert).where(
                Alert.symbol == symbol,
                Alert.is_active == True
            ).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def get_all_active(self) -> list[Alert]:
        result = await self.session.execute(
            select(Alert).where(
                Alert.is_active == True
            ).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id_and_user(self, alert_id: int, user_id: int):
        stmt = (
            select(Alert)
            .where(
                Alert.id == alert_id,
                Alert.user_id == user_id,
                Alert.is_active == True,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate(self, alert_id: int) -> bool:
        result = await self.session.execute(
            update(Alert)
            .where(Alert.id == alert_id)
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount > 0
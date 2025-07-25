from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
            select(Alert).where(Alert.user_id == user_id).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()
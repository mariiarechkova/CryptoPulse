import logging

from app.alerts.repository import AlertRepository
from app.alerts.models import Alert

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self._repo = alert_repo

    async def get_user_alerts(self, user_id: int):
        return await self._repo.get_all(user_id)

    async def create(self, symbol: str, price: float, user_id: int, direction: str) -> Alert:
        return await self._repo.create(symbol, price, user_id, direction)

    async def deactivate_alert(self, alert_id, user_id) -> tuple[bool, str | None]:
        alert = await self._repo.get_by_id_and_user(alert_id, user_id)
        if alert is None:
            return False, None

        symbol = alert.symbol
        updated = await self._repo.deactivate(alert.id)
        if not updated:
            return False, None

        return True, symbol
import logging

from app.alerts.repository import AlertRepository
from app.alerts.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class PriceUpdateService:
    def __init__(self, session_factory, bot):
        self._session_factory = session_factory
        self.notifier = NotificationService(bot)

    async def _trigger_alert(self, alert, current_price: float) -> None:
        await self.notifier.notify_price_hit(
            user_id=alert.user_id,
            symbol=alert.symbol,
            target_price=alert.target_price,
            current_price=current_price,
            direction=alert.direction,
        )
        async with self._session_factory() as session:
            repo = AlertRepository(session)
            await repo.deactivate(alert.id)

    async def check_price_update(self, symbol: str, current_price: float) -> None:
        async with self._session_factory() as session:
            repo = AlertRepository(session)
            alerts = await repo.get_active_for_symbol(symbol)

        if not alerts:
            logger.debug(f"No active alerts for {symbol}")
            return

        for alert in alerts:
            if alert.direction == 'up' and current_price >= alert.target_price:
                logger.info(f"Alert {alert.id} triggered: {symbol} ↑ {current_price}")
                await self._trigger_alert(alert, current_price)

            elif alert.direction == 'down' and current_price <= alert.target_price:
                logger.info(f"Alert {alert.id} triggered: {symbol} ↓ {current_price}")
                await self._trigger_alert(alert, current_price)
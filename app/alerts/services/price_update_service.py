import logging

from app.alerts.repository import AlertRepository
from app.alerts.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class PriceUpdateService:
    def __init__(self, alert_repo: AlertRepository, bot, subscription_manager):
            self.notifier = NotificationService(bot)
            self.subscription_manager = subscription_manager
            self._alert_repo = alert_repo

    async def _trigger_alert(self, alert, current_price: float) -> None:
        await self.notifier.notify_price_hit(
            user_id=alert.user_id,
            symbol=alert.symbol,
            target_price=alert.target_price,
            current_price=current_price,
            direction=alert.direction,
        )
        await self._alert_repo.deactivate(alert.id)

        await self.subscription_manager.stop_tracking(alert.symbol)

    async def check_price_update(self, symbol: str, current_price: float) -> None:
        alerts = await self._alert_repo.get_active_for_symbol(symbol)

        if not alerts:
            logger.debug("No active alerts for %s", symbol)
            return

        for alert in alerts:
            if alert.direction == "up" and current_price >= alert.target_price:
                logger.info("Alert %s triggered: %s ↑ %s", alert.id, symbol, current_price)
                await self._trigger_alert(alert, current_price)

            elif alert.direction == "down" and current_price <= alert.target_price:
                logger.info("Alert %s triggered: %s ↓ %s", alert.id, symbol, current_price)
                await self._trigger_alert(alert, current_price)

    async def warmup_subscriptions(self) -> None:
        alerts = await self._alert_repo.get_all_active()

        for alert in alerts:
            await self.subscription_manager.ensure_tracking(alert.symbol)

        logger.info("Warmup done, restored %d alerts", len(alerts))
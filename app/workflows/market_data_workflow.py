import logging

from app.market.models import Timeframe

logger = logging.getLogger(__name__)

class MarketDataWorkflow:
    def __init__(self, alert_service, subscription_manager, candle_service, bybit_rest_client):
        self._bybit_rest_client = bybit_rest_client
        self._alert_service = alert_service
        self._subscription_manager = subscription_manager
        self._candle_service = candle_service

    async def create_alert_and_subscribe(self, user_id: int, symbol: str, price: float, direction: str):
        alert = await self._alert_service.create(
            user_id=user_id,
            symbol=symbol,
            price=price,
            direction=direction,
        )
        await self._subscription_manager.ensure_tracking(symbol)

        return alert

    async def deactivate_alert_and_unsubscribe(self, alert_id: int, user_id: int) -> bool:
        ok, symbol = await self._alert_service.deactivate_alert(alert_id, user_id)
        if not ok:
            return False

        await self._subscription_manager.stop_tracking(symbol)
        return True

    async def download_daily_candles(self, symbol: str) -> bool:
        has_any = await self._candle_service.has_any(
            symbol=symbol,
            timeframe=Timeframe.D1,
        )
        if has_any:
            return True

        candles = await self._bybit_rest_client.fetch_d1_history(symbol=symbol)

        if not candles:
            logger.warning("No daily candles returned from REST for %s", symbol)
            return False

        await self._candle_service.save_many(
            symbol=symbol,
            timeframe=Timeframe.D1,
            candles=candles,
        )
        return False

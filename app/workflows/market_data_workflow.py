import logging
from datetime import timedelta, datetime, UTC

from app.market.models import Timeframe
from app.market.services.candle_service import LEVELS_CANDLE_WINDOWS
from infrastructure.bybit.manager import SubscriptionManager

logger = logging.getLogger(__name__)

_TF_DELTA = {
    Timeframe.H1: timedelta(hours=1),
    Timeframe.H4: timedelta(hours=4),
    Timeframe.D1: timedelta(days=1),
}

TAIL_LIMIT = 50

class MarketDataWorkflow:
    def __init__(self, alert_service, subscription_manager: SubscriptionManager | None, candle_service, bybit_rest_client):
        self._bybit_rest_client = bybit_rest_client
        self._alert_service = alert_service
        self._subscription_manager = subscription_manager
        self._candle_service = candle_service

    async def create_alert_and_subscribe(
        self, telegram_id: int, symbol: str, price: float, direction: str
    ):
        alert = await self._alert_service.create(
            telegram_id=telegram_id,
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

    async def _fetch_and_save(self, *, symbol: str, timeframe: Timeframe, limit: int) -> bool:
        candles = await self._bybit_rest_client.fetch_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
        if not candles:
            logger.warning("No candles returned from REST for %s %s", symbol, timeframe)
            return False

        await self._candle_service.save_many(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
        )
        keep_last = LEVELS_CANDLE_WINDOWS[timeframe]
        deleted = await self._candle_service.delete_old(
            symbol=symbol,
            timeframe=timeframe,
            keep_last=keep_last,
        )
        logger.info("candles.retention symbol=%s tf=%s deleted=%d keep_last=%d", symbol, timeframe, deleted, keep_last)

        return True

    async def ensure_candles(self, symbol: str, timeframe: Timeframe) -> bool:
        limit = LEVELS_CANDLE_WINDOWS.get(timeframe)
        if limit is None:
            raise ValueError(f"Unsupported timeframe for levels: {timeframe}")

        tf_delta = _TF_DELTA[timeframe]
        now = datetime.now(UTC)

        has_enough = await self._candle_service.has_at_least(symbol=symbol, timeframe=timeframe, n=limit)
        if not has_enough:
            return await self._fetch_and_save(symbol=symbol, timeframe=timeframe, limit=limit)

        last_open_time = await self._candle_service.get_latest_open_time(symbol=symbol, timeframe=timeframe)
        if last_open_time is None:
            logger.error("Invariant broken: has_at_least=True but no last candle symbol=%s tf=%s", symbol, timeframe)
            return await self._fetch_and_save(symbol=symbol, timeframe=timeframe, limit=limit)

        gap = now - last_open_time
        window_span = tf_delta * limit

        if gap > window_span:
            return await self._fetch_and_save(symbol=symbol, timeframe=timeframe, limit=limit)

        if gap > tf_delta * 2:
            return await self._fetch_and_save(symbol=symbol, timeframe=timeframe, limit=50)

        return True

    async def get_candles_for_levels(self, *, symbol: str, timeframe: Timeframe):
        await self.ensure_candles(symbol, timeframe)
        return await self._candle_service.get_for_levels(symbol=symbol, timeframe=timeframe)

import asyncio
import logging
from collections import Counter

from infrastructure.bybit.websocket_client import BybitWebSocketClient

logger = logging.getLogger(__name__)

class SubscriptionManager:
    def __init__(self, ws_client: BybitWebSocketClient):
        self.ws_client = ws_client
        self._lock = asyncio.Lock()
        self._refcount = Counter()

    async def ensure_tracking(self, symbol: str) -> None:
        async with self._lock:
            prev_count = self._refcount[symbol]
            self._refcount[symbol] += 1

        if prev_count == 0:
            await self.ws_client.subscribe_symbol(symbol)
            logger.info(f"Started tracking {symbol}")
        else:
            logger.debug(f"{symbol} already tracked (count={self._refcount[symbol]})")

    async def stop_tracking(self, symbol: str) -> None:
        async with self._lock:
            if self._refcount[symbol] > 0:
                self._refcount[symbol] -= 1
            current = self._refcount[symbol]

        if current == 0:
            await self.ws_client.unsubscribe_symbol(symbol)
            logger.info(f"Stopped tracking {symbol}")
        else:
            logger.debug(f"Still tracking {symbol} (count={current})")

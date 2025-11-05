import logging
from typing import Set

from infrastructure.bybit.websocket_client import BybitWebSocketClient

logger = logging.getLogger(__name__)

class SubscriptionManager:
    def __init__(self, ws_client: BybitWebSocketClient):
        self.ws_client = ws_client
        self.active_symbols: Set[str] = set()

    async def ensure_tracking(self, symbol: str) -> None:
        if symbol in self.active_symbols:
            logger.debug(f"Already tracking {symbol}")
            return

        await self.ws_client.subscribe_symbol(symbol)
        self.active_symbols.add(symbol)
        logger.info(f"Now tracking {symbol}")


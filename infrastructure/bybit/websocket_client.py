import asyncio
import json
import logging

import websockets

BYBIT_WS_PUBLIC_URL = "wss://stream.bybit.com/v5/public/spot"
logger = logging.getLogger(__name__)

class BybitWebSocketClient:
    def __init__(self):
        self._ws = None
        self._on_price_update = None

    async def connect(self, on_price_update):
        self._on_price_update = on_price_update

        logger.info("Connecting to Bybit WS...")
        self._ws = await websockets.connect(BYBIT_WS_PUBLIC_URL)
        logger.info("Connected.")

        await asyncio.gather(
            self._listen_loop(),
            self._heartbeat_loop(),
        )

    async def wait_until_connected(self):
        while self._ws is None:
            await asyncio.sleep(0.05)

    async def subscribe_symbol(self, symbol: str):
        msg = {
            "op": "subscribe",
            "args": [f"tickers.{symbol}"],
        }
        await self._ws.send(json.dumps(msg))
        logger.info(f"Subscribed to {symbol}")

    async def unsubscribe_symbol(self, symbol: str):
        msg = {
            "op": "unsubscribe",
            "args": [f"tickers.{symbol}"],
        }
        await self._ws.send(json.dumps(msg))
        logger.info(f"Unsubscribed from {symbol}")

    async def _listen_loop(self):
        async for raw_msg in self._ws:
            try:
                msg = json.loads(raw_msg)
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON message: {raw_msg}")
                continue

            await self._handle_message(msg)

    async def _heartbeat_loop(self):
        while True:
            ping_msg = {"op": "ping"}
            try:
                await self._ws.send(json.dumps(ping_msg))
                logger.debug("Sent ping")
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                break

            await asyncio.sleep(20)

    async def _handle_message(self, msg: dict):
        topic = msg.get("topic")
        if not topic:
            logger.debug(f"Control message: {msg}")
            return

        if topic.startswith("tickers."):
            data = msg.get("data")
            if not data:
                return
            symbol = data.get("symbol")
            last_price = data.get("lastPrice")

            if symbol is None or last_price is None:
                return

            try:
                price_val = float(last_price)
            except ValueError:
                logger.warning(f"Bad price {last_price} for {symbol}")
                return

            logger.info(f"{symbol} price update: {price_val}")
            if self._on_price_update is not None:
                await self._on_price_update(symbol, price_val)

    async def close(self):
        if self._ws is not None:
            try:
                await self._ws.close()
                logger.info("WebSocket closed.")
            except Exception as e:
                logger.warning(f"Error while closing WebSocket: {e}")
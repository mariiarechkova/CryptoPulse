import asyncio
import json
import logging

import websockets
from websockets import ConnectionClosed

BYBIT_WS_PUBLIC_URL = "wss://stream.bybit.com/v5/public/spot"
logger = logging.getLogger(__name__)

class BybitWebSocketClient:
    def __init__(self):
        self._ws = None
        self._on_price_update = None

        self._send_lock = asyncio.Lock()
        self._subscribed: set[str] = set()

        self._stop = asyncio.Event()

    async def connect(self, on_price_update):
        self._on_price_update = on_price_update

        backoff = 1

        while not self._stop.is_set():
            try:
                logger.info("Connecting to Bybit WS...")
                self._ws = await websockets.connect(
                    BYBIT_WS_PUBLIC_URL,
                    ping_interval=None,
                    close_timeout=10,
                    max_queue=1024,
                )
                logger.info("Connected.")
                backoff = 1

                await self._resubscribe_all()

                listen_task = asyncio.create_task(self._listen_loop())
                hb_task = asyncio.create_task(self._heartbeat_loop())

                done, pending = await asyncio.wait(
                    {listen_task, hb_task},
                    return_when=asyncio.FIRST_EXCEPTION,
                )

                for t in pending:
                    t.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

                for t in done:
                    exc = t.exception()
                    if exc:
                        raise exc

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"WS crashed: {e}. Reconnecting in {backoff}s...")

            await self.close()

            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)

    async def stop(self):
        self._stop.set()
        await self.close()

    async def wait_until_connected(self):
        while self._ws is None:
            await asyncio.sleep(0.05)

    async def subscribe_symbol(self, symbol: str):
        self._subscribed.add(symbol)

        if self._ws is None:
            return

        msg = {"op": "subscribe", "args": [f"tickers.{symbol}"]}
        await self._send(msg)
        logger.info(f"Subscribed to {symbol}")

    async def unsubscribe_symbol(self, symbol: str):
        self._subscribed.discard(symbol)

        if self._ws is None:
            return

        msg = {"op": "unsubscribe", "args": [f"tickers.{symbol}"]}
        await self._send(msg)
        logger.info(f"Unsubscribed from {symbol}")

    async def _send(self, msg: dict):
        if self._ws is None:
            raise RuntimeError("WebSocket not connected")

        async with self._send_lock:
            await self._ws.send(json.dumps(msg))

    async def _resubscribe_all(self):
        if not self._subscribed or self._ws is None:
            return

        args = [f"tickers.{s}" for s in self._subscribed]
        await self._send({"op": "subscribe", "args": args})
        logger.info(f"Resubscribed: {len(self._subscribed)} symbols")

    async def _listen_loop(self):
        try:
            async for raw_msg in self._ws:
                try:
                    msg = json.loads(raw_msg)
                except json.JSONDecodeError:
                    logger.warning(f"Non-JSON message: {raw_msg}")
                    continue

                await self._handle_message(msg)

        except ConnectionClosed as e:
            raise e

    async def _heartbeat_loop(self):
        while True:
            try:
                await self._send({"op": "ping"})
                logger.debug("Sent ping")
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                raise

            await asyncio.sleep(20)

    async def _handle_message(self, msg: dict):
        topic = msg.get("topic")
        if not topic:
            logger.debug(f"Control message: {msg}")
            return

        if topic.startswith("tickers."):
            data = msg.get("data") or {}
            symbol = data.get("symbol")
            last_price = data.get("lastPrice")

            if symbol is None or last_price is None:
                return

            try:
                price_val = float(last_price)
            except ValueError:
                logger.warning(f"Bad price {last_price} for {symbol}")
                return

            logger.debug(f"{symbol} price update: {price_val}")
            if self._on_price_update is not None:
                await self._on_price_update(symbol, price_val)

    async def close(self):
        if self._ws is not None:
            try:
                await self._ws.close()
                logger.info("WebSocket closed.")
            except Exception as e:
                logger.warning(f"Error while closing WebSocket: {e}")
            finally:
                self._ws = None
from datetime import datetime, timezone
from typing import Any
import httpx

from app.market.models import Timeframe


class BybitRestClient:
    _TF_TO_INTERVAL: dict[Timeframe, str] = {
        Timeframe.D1: "D",
        Timeframe.H4: "240",  # 4h = 240 minutes
        Timeframe.H1: "60",   # 1h = 60 minutes
    }

    def __init__(self, base_url: str, category: str = "spot", timeout_s: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._category = category
        self._timeout = timeout_s

    async def fetch_history(self, symbol: str, timeframe: Timeframe, limit: int) -> list[dict[str, Any]]:
        symbol = symbol.upper()
        bybit_interval = self._TF_TO_INTERVAL[timeframe]

        safe_limit = max(1, min(1000, int(limit)))

        url = f"{self._base_url}/v5/market/kline"
        params = {
            "category": self._category,
            "symbol": symbol,
            "interval": bybit_interval,
            "limit": safe_limit,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if data.get("retCode") != 0:
            raise RuntimeError(f"Bybit error retCode={data.get('retCode')}: {data.get('retMsg')}")

        rows = (data.get("result") or {}).get("list") or []

        candles: list[dict[str, Any]] = []
        for row in rows:
            # row expected: [startTime, open, high, low, close, volume, turnover] (strings)
            open_ms = int(row[0])
            candles.append(
                {
                    "open_time": datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]) if row[5] is not None else None,
                }
            )

        candles.sort(key=lambda c: c["open_time"])
        return candles

    async def fetch_d1_history(self, symbol: str, days: int = 365) -> list[dict[str, Any]]:
        return await self.fetch_history(symbol=symbol, timeframe=Timeframe.D1, limit=days)

from app.market.models import Timeframe
from app.market.repository import CandleRepository


class CandleService:
    def __init__(self, *, candle_repo: CandleRepository) -> None:
        self._repo = candle_repo

    async def has_any(self, *, symbol: str, timeframe: Timeframe) -> bool:
        return await self._repo.has_any(symbol=symbol.upper(), timeframe=timeframe)

    async def save_many(self, symbol: str, timeframe: Timeframe, candles: list[dict]) -> None:
        await self._repo.insert_many(
            symbol=symbol.upper(),
            timeframe=timeframe,
            candles=candles,
        )
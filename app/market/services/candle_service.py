from app.market.models import Timeframe
from app.market.repository import CandleRepository

LEVELS_CANDLE_WINDOWS: dict[Timeframe, int] = {
    Timeframe.H1: 960,  # ~40 days
    Timeframe.H4: 900,  # ~5 months
    Timeframe.D1: 365,  # ~1 year
}


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

    async def get_for_levels(self, *, symbol: str, timeframe: Timeframe):
        limit = LEVELS_CANDLE_WINDOWS.get(timeframe)
        if limit is None:
            raise ValueError(f"Unsupported timeframe for levels: {timeframe}")

        return await self._repo.get_latest(
            symbol=symbol.upper(),
            timeframe=timeframe,
            limit=limit,
        )

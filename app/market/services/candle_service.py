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

    async def has_at_least(self, *, symbol: str, timeframe: Timeframe, n: int) -> bool:
        return await self._repo.has_at_least(symbol=symbol.upper(), timeframe=timeframe, n=n)

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

    async def get_latest_open_time(self, *, symbol: str, timeframe: Timeframe):
        rows = await self._repo.get_latest(
            symbol=symbol.upper(),
            timeframe=timeframe,
            limit=1,
        )
        return rows[-1].open_time if rows else None

    async def delete_old(
            self, *, symbol: str, timeframe: Timeframe, keep_last: int
    ) -> int:
        cutoff = await self._repo.get_cutoff_open_time(
            symbol=symbol.upper(),
            timeframe=timeframe,
            keep_last=keep_last,
        )
        if cutoff is None:
            return 0

        return await self._repo.delete_older_than(
            symbol=symbol.upper(),
            timeframe=timeframe,
            cutoff_open_time=cutoff,
        )

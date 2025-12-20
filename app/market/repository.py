from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import insert

from app.market.models import Candle, Timeframe


class CandleRepository:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    async def has_any(self, symbol: str, timeframe: Timeframe) -> bool:
        async with self._session_factory() as session:
            stmt = (
                select(Candle.id)
                .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
                .limit(1)
            )
            res = await session.execute(stmt)
            return res.scalar_one_or_none() is not None

    async def insert_many(self, symbol: str, timeframe: Timeframe, candles: list[dict]) -> None:
        if not candles:
            return

        values = [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                **c,
            }
            for c in candles
        ]

        stmt = (
            insert(Candle)
            .values(values)
            .on_conflict_do_nothing(index_elements=["symbol", "timeframe", "open_time"])
        )

        async with self._session_factory() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_latest(self, symbol: str, timeframe: Timeframe, limit: int) -> list[Candle]:
        if limit <= 0:
            return []

        async with self._session_factory() as session:
            stmt = (
                select(Candle)
                .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
                .order_by(desc(Candle.open_time))
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()

        return list(reversed(rows))

from sqlalchemy import desc, select, delete
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

    async def has_at_least(self, *, symbol: str, timeframe: Timeframe, n: int) -> bool:
        if n <= 0:
            return True

        async with self._session_factory() as session:
            stmt = (
                select(Candle.id)
                .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
                .order_by(desc(Candle.open_time))
                .limit(n)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return len(rows) >= n


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

    async def get_cutoff_open_time(self, *, symbol: str, timeframe: Timeframe, keep_last: int):
        if keep_last <= 0:
            return None

        async with self._session_factory() as session:
            stmt = (
                select(Candle.open_time)
                .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
                .order_by(desc(Candle.open_time))
                .offset(keep_last - 1)
                .limit(1)
            )
            return (await session.execute(stmt)).scalar_one_or_none()

    async def delete_older_than(self, *, symbol: str, timeframe: Timeframe, cutoff_open_time) -> int:
        async with self._session_factory() as session:
            stmt = (
                delete(Candle)
                .where(
                    Candle.symbol == symbol,
                    Candle.timeframe == timeframe,
                    Candle.open_time < cutoff_open_time,
                )
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount or 0

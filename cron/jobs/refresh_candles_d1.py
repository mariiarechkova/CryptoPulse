from app.market.models import Timeframe
from cron.jobs.refresh_candles_tf import refresh_candles_tf


async def refresh_candles_d1(*, session_factory) -> None:
    await refresh_candles_tf(session_factory=session_factory, timeframe=Timeframe.D1)
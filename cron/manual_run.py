import asyncio
import logging

from app.market.models import Timeframe
from cron.jobs.refresh_candles_tf import refresh_candles_tf
from infrastructure.db.session import async_session_maker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def main():
    await refresh_candles_tf(
        session_factory=async_session_maker,
        timeframe=Timeframe.H1,
    )


if __name__ == "__main__":
    asyncio.run(main())
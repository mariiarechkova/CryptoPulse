import asyncio
import logging
import signal
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cron.jobs.refresh_candles_d1 import refresh_candles_d1
from cron.jobs.refresh_candles_h1 import refresh_candles_h1
from cron.jobs.refresh_candles_h4 import refresh_candles_h4
from infrastructure.db.session import async_session_maker

logger = logging.getLogger(__name__)

STOP_EVENT = asyncio.Event()

def _setup_signals() -> None:
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, STOP_EVENT.set)
        except NotImplementedError:
            signal.signal(sig, lambda *_: STOP_EVENT.set())


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    _setup_signals()

    scheduler = AsyncIOScheduler(timezone=ZoneInfo("UTC"))
    scheduler.add_job(
        refresh_candles_h1,
        trigger="cron",
        minute=2,
        id="refresh_candles_h1",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
        kwargs={"session_factory": async_session_maker},
    )

    scheduler.add_job(
        refresh_candles_h4,
        trigger="cron",
        hour="*/4",
        minute=6,
        id="refresh_candles_h4",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
        kwargs={"session_factory": async_session_maker},
    )

    scheduler.add_job(
        refresh_candles_d1,
        trigger="cron",
        hour=0,
        minute=12,
        id="refresh_candles_d1",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1800,
        kwargs={"session_factory": async_session_maker},
    )

    scheduler.start()
    logger.info("cron.started job=refresh_active_alerts_candles interval=5m")

    await STOP_EVENT.wait()

    logger.info("cron.stopping")
    scheduler.shutdown(wait=False)
    logger.info("cron.stopped")


if __name__ == "__main__":
    asyncio.run(main())
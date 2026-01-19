import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.alerts.repository import AlertRepository
from app.alerts.services.alert_service import AlertService
from app.config import settings
from app.market.models import Timeframe
from app.market.repository import CandleRepository
from app.market.services.candle_service import CandleService
from app.workflows.market_data_workflow import MarketDataWorkflow
from cron.locks import advisory_unlock, try_advisory_lock
from infrastructure.bybit.rest_client import BybitRestClient

LOCK_KEY = 9001
logger = logging.getLogger(__name__)


async def refresh_candles_tf(
    *,
    session_factory: async_sessionmaker[AsyncSession],
    timeframe: Timeframe,
) -> None:
    started = time.perf_counter()

    try:
        async with session_factory() as session:
            locked = await try_advisory_lock(session, LOCK_KEY)
            if not locked:
                logger.info("cron.skip lock_busy tf=%s key=%s", timeframe, LOCK_KEY)
                return

            try:
                alert_repo = AlertRepository(session_factory)
                candle_repo = CandleRepository(session_factory)

                candle_service = CandleService(candle_repo=candle_repo)
                alert_service = AlertService(alert_repo=alert_repo, session_factory=session_factory)

                bybit_rest_client = BybitRestClient(
                    base_url=settings.BYBIT_BASE_URL,
                    category="spot",
                    timeout_s=15.0,
                )

                market_data = MarketDataWorkflow(
                    alert_service=alert_service,
                    subscription_manager=None,
                    candle_service=candle_service,
                    bybit_rest_client=bybit_rest_client,
                )

                symbols = await alert_service.list_active_symbols()
                if not symbols:
                    logger.info("cron.tick tf=%s symbols=0", timeframe)
                    return

                success = 0
                failed = 0

                for symbol in symbols:
                    try:
                        result = await market_data.ensure_candles(
                            symbol=symbol, timeframe=timeframe
                        )
                        if result:
                            success += 1
                        else:
                            failed += 1
                            logger.warning("cron.ensure_failed tf=%s symbol=%s", timeframe, symbol)
                    except Exception:
                        failed += 1
                        logger.exception("cron.ensure_exception tf=%s symbol=%s", timeframe, symbol)

                logger.info(
                    "cron.tick_done tf=%s symbols=%d success=%d failed=%d",
                    timeframe,
                    len(symbols),
                    success,
                    failed,
                )

            finally:
                await advisory_unlock(session, LOCK_KEY)

    except Exception:
        logger.exception("cron.tick_failed tf=%s", timeframe)
    finally:
        elapsed = time.perf_counter() - started
        logger.info("cron.tick_finished tf=%s elapsed=%.2fs", timeframe, elapsed)

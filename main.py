import asyncio
import contextlib
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

from app.alerts.formatters.levels_text_formatter import LevelsPlainFormatter
from app.alerts.formatters.price_hit_formatter import PriceHitFormatter
from app.alerts.repository import AlertRepository
from app.alerts.services.alert_message_builder import AlertMessageBuilder
from app.alerts.services.alert_service import AlertService
from app.alerts.services.price_update_service import PriceUpdateService
from app.bot.routers import setup_router
from app.config import settings
from app.market.levels.atr_calculator import ATRCalculator
from app.market.levels.level_classifier import LevelClassifier
from app.market.levels.level_clusterer import LevelClusterer
from app.market.levels.pivot_detector import PivotDetector
from app.market.repository import CandleRepository
from app.market.services.candle_service import CandleService
from app.workflows.levels_workflow import LevelsWorkflow
from app.workflows.market_data_workflow import MarketDataWorkflow
from infrastructure.bybit.manager import SubscriptionManager
from infrastructure.bybit.rest_client import BybitRestClient
from infrastructure.bybit.websocket_client import BybitWebSocketClient
from infrastructure.db.session import async_session_maker
from infrastructure.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("main")
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def main():
    logger.info("Logging configured successfully!")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    ws_client = BybitWebSocketClient()
    rest_client = BybitRestClient(base_url=settings.BYBIT_BASE_URL)

    subscription_manager = SubscriptionManager(ws_client)

    alert_repo = AlertRepository(async_session_maker)
    alert_service = AlertService(alert_repo=alert_repo)

    candle_repo = CandleRepository(async_session_maker)
    candle_service = CandleService(candle_repo=candle_repo)

    # Levels stack + formatters

    atr_calculator = ATRCalculator()
    pivot_detector = PivotDetector()
    level_clusterer = LevelClusterer()
    level_classifier = LevelClassifier()

    levels_workflow = LevelsWorkflow(
        atr_calculator=atr_calculator,
        pivot_detector=pivot_detector,
        level_clusterer=level_clusterer,
        level_classifier=level_classifier,
    )

    price_hit_formatter = PriceHitFormatter()
    levels_formatter = LevelsPlainFormatter()

    alert_message_builder = AlertMessageBuilder(
        price_hit_formatter=price_hit_formatter,
        levels_formatter=levels_formatter,
        candle_service=candle_service,
        levels_workflow=levels_workflow,
    )

    price_update_service = PriceUpdateService(
        alert_repo=alert_repo,
        bot=bot,
        subscription_manager=subscription_manager,
        alert_message_builder=alert_message_builder,
    )

    market_data_workflow = MarketDataWorkflow(
        bybit_rest_client=rest_client,
        alert_service=alert_service,
        subscription_manager=subscription_manager,
        candle_service=candle_service,
    )

    dp.include_router(setup_router(alert_service, market_data_workflow))

    logger.info("Bot and WS are starting...")

    ws_task = None
    try:
        ws_task = asyncio.create_task(ws_client.connect(price_update_service.check_price_update))
        await ws_client.wait_until_connected()

        await price_update_service.warmup_subscriptions()

        await dp.start_polling(bot)

    except asyncio.CancelledError:
        logger.warning("Cancelled.")
        raise
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if ws_task:
            ws_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await ws_task
        try:
            await ws_client.close()
        except Exception:
            logger.exception("WS close failed")
        await bot.session.close()
        logger.info("Bot stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("⏹️ Interrupted by user. Exiting...")

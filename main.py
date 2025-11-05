import asyncio
import contextlib
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.alerts.services.alert_service import CreateAlertService
from app.alerts.services.price_update_service import PriceUpdateService
from app.bot.routers import setup_router
from infrastructure.bybit.manager import SubscriptionManager
from infrastructure.bybit.websocket_client import BybitWebSocketClient
from infrastructure.db.session import get_session, async_session_maker
from infrastructure.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("main")
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    logger.info("Logging configured successfully!")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    price_update_service = PriceUpdateService(
        session_factory=async_session_maker,
        bot=bot,
    )

    ws_client = BybitWebSocketClient(price_update_service)
    subscription_manager = SubscriptionManager(ws_client)

    create_alert_service = CreateAlertService(
        session_factory=async_session_maker,
        subscription_manager=subscription_manager,
    )

    dp.include_router(setup_router(create_alert_service))

    logger.info("Bot and WS are starting...")

    ws_task = None
    try:
        ws_task = asyncio.create_task(ws_client.connect())
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

import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.bot.routers import setup_router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def main():
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(setup_router())

    print("🚀 Bot is running...")
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("🛑 Polling cancelled.")
    finally:
        await bot.session.close()
        print("✅ Bot stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ Interrupted by user. Exiting...")

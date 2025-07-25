
import asyncio
import os

from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

from app.bot.routers import setup_router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher()
    dp.include_router(setup_router())

    print("The bot is running")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
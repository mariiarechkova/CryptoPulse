from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Это бот. Напиши /help для команд.")

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer("Доступные команды :\n/start — начать\n/help — помощь")
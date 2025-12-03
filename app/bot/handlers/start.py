from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards import main_menu_keyboard

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer("Готов следить за рынком ⚡ \nВыберите, что хотите сделать:",
                         reply_markup=main_menu_keyboard())

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer("Доступные команды :\n/start — начать\n/help — помощь")
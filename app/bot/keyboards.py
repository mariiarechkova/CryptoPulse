from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои алерты"), KeyboardButton(text="🗑 Удалить алерт")],
            [KeyboardButton(text="➕ Создать алерт")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def confirm_delete_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, удалить"), KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
    )
    return keyboard

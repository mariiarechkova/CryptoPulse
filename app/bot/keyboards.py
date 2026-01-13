from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои алерты"), KeyboardButton(text="➕ Создать алерт")],
            [KeyboardButton(text="📐 Рассчитать уровни"), KeyboardButton(text="🗑 Удалить алерт")]
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

def buy_subscription_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Купить подписку", callback_data="buy_subscription")]
        ]
    )
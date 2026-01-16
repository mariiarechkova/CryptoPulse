from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои алерты"), KeyboardButton(text="➕ Создать алерт")],
            [KeyboardButton(text="📐 Рассчитать уровни"), KeyboardButton(text="🗑 Удалить алерт")],
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

def levels_tf_kb(symbol: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🕐 1H", callback_data=f"levels_tf:{symbol}:H1"),
            InlineKeyboardButton(text="🕓 4H", callback_data=f"levels_tf:{symbol}:H4"),
            InlineKeyboardButton(text="📅 1D", callback_data=f"levels_tf:{symbol}:D1"),
        ]
    ])

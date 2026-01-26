from aiogram.types import Message

from app.bot.keyboards import buy_subscription_kb, main_menu_keyboard
from app.market.models import Timeframe


class LevelsCallbackService:
    # parsing / validation

    def extract_symbol(self, *, fsm_data: dict) -> str | None:
        symbol = fsm_data.get("symbol")
        return symbol if isinstance(symbol, str) and symbol else None

    def parse_tf_code(self, *, callback_data: str) -> str | None:
        # levels_tf:{symbol}:H1
        try:
            _, _, tf_code = callback_data.split(":")
        except ValueError:
            return None
        return tf_code

    def parse_timeframe(self, *, tf_code: str) -> Timeframe | None:
        try:
            return Timeframe(tf_code)
        except ValueError:
            return None

    # replies

    async def reply_symbol_missing(self, *, message: Message) -> None:
        await message.answer(
            "Символ не найден. Попробуй ещё раз.",
            reply_markup=main_menu_keyboard(),
        )

    async def reply_bad_timeframe(self, *, message: Message) -> None:
        await message.answer(
            "Не удалось прочитать таймфрейм. Попробуй ещё раз.",
            reply_markup=main_menu_keyboard(),
        )

    async def reply_unknown_timeframe(self, *, message: Message) -> None:
        await message.answer(
            "Неизвестный таймфрейм. Попробуй ещё раз.",
            reply_markup=main_menu_keyboard(),
        )

    async def reply_demo_limit(self, *, message: Message) -> None:
        await message.answer(
            "Лимит демо-расчётов уровней исчерпан. Оформи подписку, чтобы считать уровни без ограничений.",
            reply_markup=buy_subscription_kb(),
        )

    async def reply_build_error(self, *, message: Message) -> None:
        await message.answer(
            "Не удалось рассчитать уровни 😕\n" "Попробуй другой символ или повтори попытку позже.",
            reply_markup=main_menu_keyboard(),
        )

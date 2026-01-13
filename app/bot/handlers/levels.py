from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.alerts.services.levels_manual_service import LevelsDemoLimitError
from app.alerts.services.levels_text_builder import LevelsBuildError
from app.bot.keyboards import main_menu_keyboard, buy_subscription_kb
from app.bot.parsers.parse_levels_message import parse_levels_message
from app.bot.states import LevelsStates

MENU_TEXTS = {
    "📋 Мои алерты",
    "➕ Создать алерт",
    "🗑 Удалить алерт",
    "📐 Рассчитать уровни",
}


def build_levels_router(levels_manual_service) -> Router:
    router = Router()

    @router.message(F.text == "📐 Рассчитать уровни")
    async def ask_symbol(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(LevelsStates.waiting_for_symbol)
        await message.answer("Введи торговую пару, например: BTCUSDT")

    @router.message(LevelsStates.waiting_for_symbol)
    async def handle_levels_symbol(message: Message, state: FSMContext):
        if message.text in MENU_TEXTS:
            await state.clear()
            return

        try:
            symbol = parse_levels_message(message.text)
        except ValueError as e:
            await message.answer(str(e))
            return

        try:
            text = await levels_manual_service.build_text(
                telegram_id=message.from_user.id,
                symbol=symbol,
            )
            await message.answer(text, reply_markup=main_menu_keyboard())

        except LevelsDemoLimitError:
            await message.answer(
                "Лимит демо-расчётов уровней исчерпан. Оформи подписку, чтобы считать уровни без ограничений.",
                reply_markup=buy_subscription_kb()
            )

        except LevelsBuildError:
            await message.answer(
                "Не удалось рассчитать уровни 😕\n"
                "Попробуй другой символ или повтори попытку позже.",
                reply_markup=main_menu_keyboard(),
            )

        finally:
            await state.clear()

    return router

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.alerts.services.levels_manual_service import LevelsDemoLimitError
from app.alerts.services.levels_text_builder import LevelsBuildError
from app.bot.keyboards import buy_subscription_kb, levels_tf_kb, main_menu_keyboard
from app.bot.parsers.parse_levels_message import parse_levels_message
from app.bot.states import LevelsStates
from app.market.models import Timeframe

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

        await state.update_data(symbol=symbol)
        await state.set_state(LevelsStates.waiting_for_timeframe)

        await message.answer(
            "Выбери таймфрейм для уровней:",
            reply_markup=levels_tf_kb(symbol),
        )

    @router.callback_query(LevelsStates.waiting_for_timeframe, F.data.startswith("levels_tf:"))
    async def handle_levels_timeframe(callback: CallbackQuery, state: FSMContext):
        await callback.answer()

        data = await state.get_data()
        symbol = data.get("symbol")
        if not symbol:
            await state.clear()
            await callback.message.answer(
                "Символ не найден. Попробуй ещё раз.",
                reply_markup=main_menu_keyboard(),
            )
            return

        # levels_tf:{symbol}:H1
        try:
            _, _, tf_code = callback.data.split(":")
        except ValueError:
            await state.clear()
            await callback.message.answer(
                "Не удалось прочитать таймфрейм. Попробуй ещё раз.",
                reply_markup=main_menu_keyboard(),
            )
            return

        try:
            timeframe = Timeframe(tf_code)
        except ValueError:
            await state.clear()
            await callback.message.answer(
                "Неизвестный таймфрейм. Попробуй ещё раз.",
                reply_markup=main_menu_keyboard(),
            )
            return

        try:
            text = await levels_manual_service.build_text(
                telegram_id=callback.from_user.id,
                symbol=symbol,
                timeframe=timeframe,
            )
            await callback.message.answer(text, reply_markup=main_menu_keyboard())

        except LevelsDemoLimitError:
            await callback.message.answer(
                "Лимит демо-расчётов уровней исчерпан. Оформи подписку, чтобы считать уровни без ограничений.",
                reply_markup=buy_subscription_kb(),
            )

        except LevelsBuildError:
            await callback.message.answer(
                "Не удалось рассчитать уровни 😕\n"
                "Попробуй другой символ или повтори попытку позже.",
                reply_markup=main_menu_keyboard(),
            )

        finally:
            await state.clear()

    return router

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.alerts.services.levels_callback_service import LevelsCallbackService
from app.alerts.services.levels_manual_service import LevelsDemoLimitError
from app.alerts.services.levels_text_builder import LevelsBuildError
from app.bot.keyboards import levels_tf_kb, main_menu_keyboard
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

        await state.update_data(symbol=symbol)
        await state.set_state(LevelsStates.waiting_for_timeframe)

        await message.answer(
            "Выбери таймфрейм для уровней:",
            reply_markup=levels_tf_kb(symbol),
        )

    @router.callback_query(LevelsStates.waiting_for_timeframe, F.data.startswith("levels_tf:"))
    async def handle_levels_timeframe(callback: CallbackQuery, state: FSMContext):
        await callback.answer()

        helper = LevelsCallbackService()

        fsm_data = await state.get_data()
        symbol = helper.extract_symbol(fsm_data=fsm_data)
        if not symbol:
            await state.clear()
            await helper.reply_symbol_missing(message=callback.message)
            return

        tf_code = helper.parse_tf_code(callback_data=callback.data)
        if tf_code is None:
            await state.clear()
            await helper.reply_bad_timeframe(message=callback.message)
            return

        timeframe = helper.parse_timeframe(tf_code=tf_code)
        if timeframe is None:
            await state.clear()
            await helper.reply_unknown_timeframe(message=callback.message)
            return

        try:
            text = await levels_manual_service.build_text(
                telegram_id=callback.from_user.id,
                symbol=symbol,
                timeframe=timeframe,
            )
            await callback.message.answer(text, reply_markup=main_menu_keyboard())

        except LevelsDemoLimitError:
            await helper.reply_demo_limit(message=callback.message)

        except LevelsBuildError:
            await helper.reply_build_error(message=callback.message)

        finally:
            await state.clear()

    return router

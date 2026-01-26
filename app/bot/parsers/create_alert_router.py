from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.alerts.services.alert_service import ActiveSymbolLimitError
from app.bot.keyboards import buy_subscription_kb, direction_kb, main_menu_keyboard
from app.bot.parsers.create_alert_parser import parse_direction_cb, parse_price, parse_symbol
from app.bot.states import CreateAlertStates


def build_create_alert_router(market_data_workflow) -> Router:
    router = Router()

    @router.message(F.text == "➕ Создать алерт")
    async def start(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(CreateAlertStates.waiting_for_symbol)
        await message.answer(
            "Введи торговую пару, например: BTCUSDT",
            reply_markup=ReplyKeyboardRemove(),
        )

    @router.message(CreateAlertStates.waiting_for_symbol)
    async def got_symbol(message: Message, state: FSMContext):
        try:
            symbol = parse_symbol(message.text)
        except ValueError as e:
            await message.answer(str(e))
            return

        await state.update_data(symbol=symbol)
        await state.set_state(CreateAlertStates.waiting_for_price)
        await message.answer(
            f"Ок. Теперь введи цену для {symbol}", reply_markup=ReplyKeyboardRemove()
        )

    @router.message(CreateAlertStates.waiting_for_price)
    async def got_price(message: Message, state: FSMContext):
        try:
            price = parse_price(message.text)
        except ValueError as e:
            await message.answer(str(e))
            return

        await state.update_data(target_price=price)
        await state.set_state(CreateAlertStates.waiting_for_direction)

        data = await state.get_data()
        symbol = data["symbol"]

        await message.answer(
            f"Выбери направление:\n\n{symbol} {price}",
            reply_markup=direction_kb(),
        )

    @router.callback_query(
        CreateAlertStates.waiting_for_direction,
        F.data.startswith("alert_dir:"),
    )
    async def got_direction(call: CallbackQuery, state: FSMContext):
        try:
            direction = parse_direction_cb(call.data)
        except ValueError as e:
            await call.answer(str(e), show_alert=True)
            return

        data = await state.get_data()
        symbol = data["symbol"]
        price = data["target_price"]

        try:
            alert = await market_data_workflow.create_alert_and_subscribe(
                telegram_id=call.from_user.id,
                symbol=symbol,
                price=price,
                direction=direction,
            )
            await state.clear()
            await call.answer()
            await call.message.answer(
                f"✅ Алерт сохранён: {alert.symbol} {alert.target_price} {alert.direction}",
                reply_markup=main_menu_keyboard(),
            )

        except ActiveSymbolLimitError:
            await state.clear()
            await call.answer()
            await call.message.answer(
                "В бесплатной версии можно отслеживать только одну монету.\n"
                "Оформи подписку и получи возможность отслеживать до 10 монет одновременно.",
                reply_markup=buy_subscription_kb(),
            )

    return router

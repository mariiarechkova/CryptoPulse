import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.alerts.services.alert_service import ActiveSymbolLimitError
from app.bot.keyboards import buy_subscription_kb, confirm_delete_keyboard, main_menu_keyboard
from app.bot.parsers.create_alert_parser import parse_create_alert_message
from app.bot.states import AlertStates


def build_router(create_alert_service, market_data_workflow) -> Router:
    router = Router()

    @router.message(F.text == "📋 Мои алерты")
    @router.message(Command("alerts"))
    async def list_alerts(message: Message, state: FSMContext):
        await state.clear()
        alerts = await create_alert_service.get_user_alerts(message.from_user.id)
        if not alerts:
            await message.answer("У тебя пока нет активных алертов.")
            return

        lines = [
            f"{idx}. {a.created_at:%H:%M} — {a.symbol} price {a.target_price} {a.direction}"
            for idx, a in enumerate(alerts, start=1)
        ]

        text = "Твои активные алерты:\n\n" + "\n".join(lines)
        await message.answer(text)

    @router.message(F.text == "➕ Создать алерт")
    async def create_alert_help(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Укажи характеристики алерта, например: \n" "BTCUSDT 105000 up/down")

    @router.message(F.text == "🗑 Удалить алерт")
    async def ask_which_alert_to_delete(message: Message, state: FSMContext):
        alerts = await create_alert_service.get_user_alerts(message.from_user.id)
        if not alerts:
            await message.answer("У тебя пока нет активных алертов для удаления.")
            return

        lines = [
            f"{idx}. {a.created_at:%H:%M} — {a.symbol} price {a.target_price} {a.direction}"
            for idx, a in enumerate(alerts, start=1)
        ]

        alerts_data = [
            {
                "id": a.id,
                "symbol": a.symbol,
                "target_price": float(a.target_price),
                "direction": a.direction,
            }
            for a in alerts
        ]
        await state.update_data(alerts=alerts_data)

        await state.set_state(AlertStates.waiting_for_alert_index)

        text = "Выбери алерт, который хочешь удалить:\n\n" + "\n".join(lines)
        text += "\n\nНапиши номер алерта:"
        await message.answer(text)

    @router.message(AlertStates.waiting_for_alert_index)
    async def handle_alert_index(message: Message, state: FSMContext):
        text = message.text.strip()
        if not text.isdigit():
            await message.answer("Введи порядковый номер алерта(число)")
            return

        index = int(text)

        data = await state.get_data()
        alerts = data["alerts"]
        if index < 1 or index > len(alerts):
            await message.answer("Введeн неверный номер алерта")
            return

        selected_alert = alerts[index - 1]

        await state.update_data(selected=selected_alert)

        await state.set_state(AlertStates.waiting_for_confirmation)

        await message.answer(
            f"Вы выбрали:\n\n"
            f"{selected_alert['symbol']} price {selected_alert['target_price']} {selected_alert['direction']}\n\n"
            "Удалить этот алерт?",
            reply_markup=confirm_delete_keyboard(),
        )

    @router.message(AlertStates.waiting_for_confirmation)
    async def confirm_delete(message: Message, state: FSMContext):
        text = message.text.lower().strip()
        user_id = message.from_user.id
        data = await state.get_data()

        ACTIONS = {
            "отмена": "cancel",
            "да, удалить": "confirm",
        }

        action = ACTIONS.get(text, "invalid")

        match action:
            case "cancel":
                await state.clear()
                await message.answer(
                    "Окей, отменяю удаление 🙂",
                    reply_markup=main_menu_keyboard(),
                )
                return

            case "confirm":
                selected = data["selected"]
                alert_id = selected["id"]
                ok = await market_data_workflow.deactivate_alert_and_unsubscribe(
                    alert_id=alert_id,
                    user_id=user_id,
                )
                await state.clear()

                reply = "Не получилось отключить алерт 😕" if not ok else "Алерт удалён 🗑️"

                await message.answer(reply, reply_markup=main_menu_keyboard())
                return

            case "invalid":
                await message.answer(
                    "Отправь: «Да, удалить» или «Отмена».",
                )

    @router.message(StateFilter(None), F.text)
    async def handle_alert_message(message: Message):
        try:
            symbol, price, direction = parse_create_alert_message(message.text)

            alert = await market_data_workflow.create_alert_and_subscribe(
                telegram_id=message.from_user.id,
                symbol=symbol,
                price=price,
                direction=direction,
            )

            await message.answer(
                f"Алерт сохранён: {alert.symbol} {alert.target_price} {alert.direction}"
            )

            asyncio.create_task(market_data_workflow.download_daily_candles(alert.symbol))

        except ActiveSymbolLimitError:
            await message.answer(
                "В бесплатной версии можно отслеживать только одну монету.\n"
                "Оформи подписку и получи возможность отслеживать до 10 монет одновременно.",
                reply_markup=buy_subscription_kb(),
            )

        except ValueError as e:
            await message.answer(str(e))

    return router

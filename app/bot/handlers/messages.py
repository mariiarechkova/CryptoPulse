from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message


def build_router(create_alert_service) -> Router:
    router = Router()

    @router.message(Command("alerts"))
    async def list_alerts(message: Message):
        alerts = await create_alert_service.get_user_alerts(message.from_user.id)
        if not alerts:
            await message.answer("Нет алертов.")
            return

        lines = [f"{a.created_at:%H:%M} — {a.symbol} price {a.target_price} {a.direction}" for a in alerts]
        await message.answer("\n".join(lines))


    @router.message(F.text)
    async def handle_alert_message(message: Message):
        try:
            alert = await create_alert_service.create_alert_from_message(message)
            await message.answer(f"Алерт сохранён: {alert.symbol} {alert.target_price} {alert.direction}")
        except ValueError as e:
            await message.answer(str(e))

    return router

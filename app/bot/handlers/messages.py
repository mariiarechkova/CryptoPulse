from aiogram import Router, F
from aiogram.types import Message

from app.alerts.service import AlertService
from app.alerts.repository import AlertRepository
from infrastructure.db.session import get_session

router = Router()


@router.message(F.text == "/alerts")
async def list_alerts(message: Message):
    async with get_session() as session:
        repo = AlertRepository(session)
        alerts = await repo.get_all(message.from_user.id)
        if not alerts:
            await message.answer("Нет алертов.")
            return

        lines = [f"{a.created_at:%H:%M} — {a.symbol} price {a.target_price}" for a in alerts]
        await message.answer("\n".join(lines))


@router.message(F.text)
async def handle_alert_message(message: Message):
    async with get_session() as session:
        service = AlertService(session)

        try:
            alert = await service.create_alert_from_message(message)
            direction_text = f" → {alert.direction}" if alert.direction else ""
            await message.answer(f"Алерт сохранен: {alert.symbol} → {alert.target_price}{direction_text}")
        except ValueError as e:
            await message.answer(str(e))


from aiogram.types import Message
from app.alerts.repository import AlertRepository
from app.alerts.models import Alert
from datetime import datetime

class AlertService:
    def __init__(self, session):
        self.repo = AlertRepository(session)

    async def create_alert_from_message(self, message: Message) -> Alert:
        text = message.text.strip()
        user_id = message.from_user.id

        parts = text.split()
        if len(parts) < 2 or len(parts) > 3:
            raise ValueError("Неверный формат. Используй, например: BTCUSDT 105000 [up/down]")

        symbol = parts[0].upper()
        price_str = parts[1]
        direction = parts[2].lower() if len(parts) == 3 else None

        if len(symbol) < 5 or not symbol.isalnum():
            raise ValueError("Некорректный тикер (например: BTCUSDT).")

        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Цена должна быть положительным числом.")

        if direction and direction not in ("up", "down"):
            raise ValueError("Направление должно быть 'up' или 'down' (или не указывать).")

        return await self.repo.create(symbol, price, user_id, direction)
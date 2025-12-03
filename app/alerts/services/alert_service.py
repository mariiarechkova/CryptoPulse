import logging

from aiogram.types import Message
from app.alerts.repository import AlertRepository
from app.alerts.models import Alert
from infrastructure.bybit.manager import SubscriptionManager

logger = logging.getLogger(__name__)

class CreateAlertService:
    def __init__(self, session_factory, subscription_manager: SubscriptionManager):
        self._session_factory = session_factory
        self.subscription = subscription_manager

    async def get_user_alerts(self, user_id: int):
        async with self._session_factory() as session:
            repo = AlertRepository(session)
            return await repo.get_all(user_id)

    async def create_alert_from_message(self, message: Message) -> Alert:
        text = message.text.strip()
        user_id = message.from_user.id

        parts = text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат. Используй, например: BTCUSDT 105000 up/down")

        symbol = parts[0].upper()
        price_str = parts[1]
        direction = parts[2].lower()

        if len(symbol) < 5 or not symbol.isalnum():
            raise ValueError("Некорректный тикер (например: BTCUSDT).")

        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Цена должна быть положительным числом.")

        if direction not in ("up", "down"):
            raise ValueError("Направление должно быть 'up' или 'down'")

        async with self._session_factory() as session:
            repo = AlertRepository(session)
            alert = await repo.create(symbol, price, user_id, direction)
        await self.subscription.ensure_tracking(symbol)
        return alert

    async def deactivate_alert(self, alert_id, user_id):
        async with self._session_factory() as session:
            repo = AlertRepository(session)
            alert = await repo.get_by_id_and_user(alert_id, user_id)
            if alert is None:
                return False

            symbol = alert.symbol

            updated = await repo.deactivate(alert.id)
            if not updated:
                return False

        await self.subscription.stop_tracking(symbol)
        return True

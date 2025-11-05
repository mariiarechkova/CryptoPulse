import logging

from aiogram import Bot

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def notify_price_hit(
        self,
        user_id: int,
        symbol: str,
        target_price: float,
        current_price: float,
        direction: str | None,
    ):

        if direction == "up":
            verb = "пробил уровень"
        elif direction == "down":
            verb = "упал ниже уровня"
        else:
            verb = "достиг твоего уровня"

        text = (
            f"{symbol} {verb} уровень {target_price:,.2f}\n"
            f"Текущая цена: {current_price:,.2f}"
        )
        logger.info(
            f"Sending alert to user {user_id}: {symbol} {verb} {target_price} "
            f"(current {current_price}, dir={direction})"
        )
        await self.bot.send_message(chat_id=user_id, text=text)
        logger.info(f"Alert delivered to user {user_id}")
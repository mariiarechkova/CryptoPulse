import logging

from aiogram import Bot

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def notify_text(self, *, user_id: int, text: str) -> None:
        logger.info("Sending alert to user %s", user_id)
        await self.bot.send_message(chat_id=user_id, text=text)
        logger.info("Alert delivered to user %s", user_id)

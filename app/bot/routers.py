from aiogram import Router
from .handlers import start, messages

def setup_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(messages.router)
    return router
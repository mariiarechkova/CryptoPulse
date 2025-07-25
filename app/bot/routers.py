from aiogram import Router
from .handlers import start

def setup_router() -> Router:
    router = Router()
    router.include_router(start.router)
    return router
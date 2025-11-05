from aiogram import Router
from .handlers import start
from .handlers.messages import build_router



def setup_router(create_alert_service):
    root = Router()
    root.include_router(start.router)
    root.include_router(build_router(create_alert_service))
    return root

from aiogram import Router

from .handlers import payments, start
from .handlers.levels import build_levels_router
from .handlers.messages import build_router
from .parsers.create_alert_router import build_create_alert_router


def setup_router(create_alert_service, market_data_workflow, levels_manual_service):
    root = Router()
    root.include_router(start.router)
    root.include_router(build_levels_router(levels_manual_service))
    root.include_router(build_create_alert_router(market_data_workflow))
    root.include_router(build_router(create_alert_service, market_data_workflow))
    root.include_router(payments.router)
    return root

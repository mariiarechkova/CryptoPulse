from aiogram.fsm.state import State, StatesGroup


class AlertStates(StatesGroup):
    waiting_for_alert_index = State()
    waiting_for_confirmation = State()

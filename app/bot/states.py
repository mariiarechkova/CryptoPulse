from aiogram.fsm.state import State, StatesGroup


class AlertStates(StatesGroup):
    waiting_for_alert_index = State()
    waiting_for_confirmation = State()


class LevelsStates(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_timeframe = State()


class CreateAlertStates(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_price = State()
    waiting_for_direction = State()

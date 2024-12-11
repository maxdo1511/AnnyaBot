from aiogram.fsm.state import StatesGroup, State


class RemindState(StatesGroup):
    message = State()
    reminder_time = State()
    delta = State()
    categories = State()
    is_complete = State()
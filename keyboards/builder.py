from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def inline(text: str | list):
    builder = InlineKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=t) for t in text]

    return builder.as_markup()


def reply(text: str | list):
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=t) for t in text]

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


remove = ReplyKeyboardRemove()

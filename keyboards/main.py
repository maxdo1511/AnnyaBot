from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Информация", callback_data="info"),
            InlineKeyboardButton(text="Помощь", callback_data="help")
        ]
    ])

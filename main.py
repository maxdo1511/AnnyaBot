import asyncio
import os
import threading
from enum import Enum

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

import handlers
import keyboards.main
from db import db
from services.reminder_service import periodic_update

# Настройка бота
API_TOKEN = os.environ.get('TOKEN')
bot = None
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
start_router = Router()


# Обработчик команды /start
@start_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот с напоминаниями. Введите /help, чтобы узнать, что я умею.",
                         reply_markup=keyboards.main.keyboard)


# Обработчик нажатия на кнопки
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "info":
        await callback.message.answer("Бот создан @dziganyaa в качестве выпускной работы курса Цифриум.")
    elif callback.data == "help":
        await callback.message.answer("======== Помощь ========\n" +
                                      "/add_remind - добавить напоминание\n" +
                                      "/remind_list - список напоминаний (сначала ближайшее)\n" +
                                      "/add_category - добавить категорию\n" +
                                      "/remind_category - список напоминаний по категориям\n" +
                                      "/help - помощь")


async def main() -> None:
    global bot
    bot = Bot(token=API_TOKEN)
    dp.include_routers(
        start_router,
        handlers.remind.router,
        handlers.default.router
    )

    asyncio.create_task(periodic_update(bot))

    await dp.start_polling(bot)


if __name__ == '__main__':
    db.main()

    asyncio.run(main())
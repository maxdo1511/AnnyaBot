from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def add_remind(message: Message):
    await message.answer("======== Помощь ========\n" +
                         "/add_remind - добавить напоминание\n" +
                         "/remind_list - список напоминаний (сначала ближайшее)\n" +
                         "/add_category - добавить категорию\n" +
                         "/remind_category - список напоминаний по категориям\n" +
                         "/help - помощь")

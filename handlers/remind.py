import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import keyboards.builder
import utils
from db import db
from services import reminder_service
from states.states import RemindState

router = Router()


@router.message(Command("remind_list"))
async def remind_list(message: Message):
    user = db.get_user_by_username(message.from_user.username)
    if user is None:
        await message.answer("Вы не зарегистрированы")
        return

    reminders = db.get_all_user_reminders(user.id)
    if not reminders:
        await message.answer("Список напоминаний пуст")
        return

    await message.answer("Список напоминаний:")
    for r in reminders:
        await message.answer(r.message)


@router.message(Command("add_remind"))
async def add_remind(message: Message, state: FSMContext):
    await state.set_state(RemindState.message)
    await message.answer("Введите текст напоминания:", reply_markup=keyboards.builder.remove)


@router.message(RemindState.message)
async def remind_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(RemindState.reminder_time)
    await message.answer("Когда у вас мероприятье?")


@router.message(RemindState.reminder_time)
async def remind_time(message: Message, state: FSMContext):
    date = utils.dateutil.parse_date_from_NL(message.text)
    if date is None:
        await message.answer("Я не понял, повторите")
        return

    await state.update_data(reminder_time=date)
    await state.set_state(RemindState.delta)
    await message.answer(
        "За сколько минут напомнить?",
        reply_markup=keyboards.builder.reply(["1", "15", "30", "60", "Не напоминать"])
    )


@router.message(RemindState.delta)
async def remind_delta(message: Message, state: FSMContext):
    if message.text == "Не напоминать":
        await state.set_state(RemindState.is_complete)
        data = await state.get_data()
        await message.answer(
            "Все верно?\n\nНапоминание: " + data['message'] + "\nНачало:" + str(data['reminder_time']),
            reply_markup=keyboards.builder.reply(["Да", "Нет"])
        )
        return
    if not message.text.isdigit():
        await message.answer("Некорректное значение. Введите число.")
        return

    await state.update_data(delta=int(message.text))
    await state.set_state(RemindState.is_complete)
    data = await state.get_data()
    await message.answer(
        "Все верно?\n\nНапоминание: " + data['message'] + "\nНачало: " + str(data['reminder_time']) + "\nНапомнить за: " + str(data['delta']) + " минут",
        reply_markup=keyboards.builder.reply(["Да", "Нет"])
    )


@router.message(RemindState.is_complete)
async def remind_is_complete(message: Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        user = db.get_user_by_telegram_id(message.from_user.id)
        await reminder_service.add_reminder(user.id, data['message'], data['reminder_time'],
                                            data['reminder_time'] - datetime.timedelta(minutes=data['delta']))
        time_to_remind = data['reminder_time'] - datetime.datetime.now()
        await message.answer("Напоминание добавлено. Сработает через " + utils.dateutil.difference_to_string(time_to_remind), reply_markup=keyboards.builder.remove)
    else:
        await message.answer("Напоминание не добавлено")
    await state.clear()
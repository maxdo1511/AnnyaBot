import asyncio
import datetime

from aiogram import Bot

import keyboards
from db import db


async def add_reminder(user_id, message, reminder_time, reminder_time_delta=None, categories=None):
    if categories is None:
        categories = ['other']

    reminder = db.Reminder(
        user_id=user_id,
        message=db.encryption.encrypt(message),
        reminder_time=reminder_time,
        reminder_time_delta=reminder_time_delta,
        created_at=datetime.datetime.now(),
        is_delta_done=reminder_time_delta is None
    )

    with db.SessionLocal() as session:
        user = session.query(db.User).filter(db.User.id == user_id).first()
        user_category_ids = [c.id for c in user.categories]
        session.add(reminder)

        for c in categories:
            category = db.get_category_by_name(c)
            if category is None:
                category = db.Category(name=c)
                session.add(category)
            else:
                category = session.merge(category)
            if category.id not in user_category_ids:
                user.categories.append(category)

            reminder.categories.append(category)

        session.commit()


async def update(bot: Bot):
    global reminds_to_repeat
    reminds = db.get_reminders_to_remind()

    for reminder in reminds:
        await sent_remindr(bot, reminder.id)


async def sent_remindr(bot: Bot, reminder_id):
    with db.SessionLocal() as session:
        reminder = session.query(db.Reminder).filter(db.Reminder.id == reminder_id).first()

        user = reminder.user
        if user is None:
            print(f"Пользователь не найден для напоминания ID {reminder.id}.")
            return

        await bot.send_message(
            user.telegram_id,
            "Вы просили напомнить: \n\n" + db.encryption.decrypt(reminder.message),
            reply_markup=keyboards.builder.inline({
                "remind_ok": "Прочитал",
                "remind_more": "Повторить",
                "remind_cancel": "Отменить"
            }, reminder.id)
        )

        now_time = datetime.datetime.now()

        #if reminder.reminder_time_delta <= now_time:
        #    reminder.is_delta_done = True
        if reminder.reminder_time <= now_time:
            reminder.is_done = True

        reminder.reminder_time_delta = now_time + datetime.timedelta(minutes=1)
        reminder.is_delta_done = False
        session.commit()




async def periodic_update(bot: Bot):
    while True:
        await update(bot)
        await asyncio.sleep(5)
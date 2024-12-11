import asyncio
import datetime

from aiogram import Bot

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
        session.add(reminder)
        session.commit()

        reminder_categories = []

        for c in categories:
            category = db.get_category_by_name(c)
            if category is None:
                category = db.Category(name=c)
                session.add(category)
                session.commit()

            reminder_category = db.ReminderCategory(
                reminder_id=reminder.id,
                category_id=category.id
            )
            reminder_categories.append(reminder_category)

        session.add_all(reminder_categories)

        session.commit()


async def update(bot: Bot):
    reminds = db.get_reminders_to_remind()

    for reminder in reminds:
        with db.SessionLocal() as session:
            reminder = session.merge(reminder)
            user = reminder.user
            await bot.send_message(user.telegram_id, "Вы просили напомнить: \n\n" + reminder.message)
            nowTime = datetime.datetime.now()
            if reminder.reminder_time_delta <= nowTime:
                reminder.is_delta_done = True
            if reminder.reminder_time <= nowTime:
                reminder.is_done = True
            session.commit()


async def periodic_update(bot: Bot):
    while True:
        await update(bot)
        await asyncio.sleep(5)
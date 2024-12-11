import datetime

from db import db
from services import reminder_service


def try_register_user(username, telegram_id):
    user = db.get_user_by_username(username)
    if user is None:
        user = db.User(username=username, telegram_id=telegram_id, created_at=datetime.datetime.now())
        with db.SessionLocal() as session:
            session.add(user)
            session.commit()


def add_reminder_to_user(telegram_user_id, reminder):
    with db.SessionLocal() as session:
        user = session.query(db.User).filter(db.User.telegram_id == telegram_user_id).first()
        if reminder.delta is not None:
            reminder_time_delta = datetime.datetime.strptime(reminder.reminder_time, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(minutes=reminder.delta)
            reminder_service.add_reminder(user.id, reminder.message, reminder.reminder_time, reminder_time_delta)
        else:
            reminder_service.add_reminder(user.id, reminder.message, reminder.reminder_time)

import os

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine, and_, Boolean, \
    or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

from db import encryption

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)  # Имя пользователя
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Дата создания пользователя

    reminders = relationship("Reminder", back_populates="user")
    categories = relationship("Category", secondary="user_categories", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', created_at='{self.created_at}')>"


class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # ID пользователя
    message = Column(String, nullable=False)  # Сообщение напоминания
    reminder_time = Column(DateTime, nullable=False)  # Время напоминания
    reminder_time_delta = Column(DateTime, nullable=True)  # Время первого напоминания
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Дата создания напоминания
    is_delta_done = Column(Boolean, default=False)  # Завершено ли первое напоминание
    is_done = Column(Boolean, default=False)  # Завершено ли напоминание

    user = relationship("User", back_populates="reminders")
    categories = relationship("Category", secondary="reminder_categories", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder(id={self.id}, user_id={self.user_id}, message='{self.message}', reminder_time='{self.reminder_time}')>"


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    reminders = relationship("Reminder", secondary="reminder_categories")
    users = relationship("User", secondary="user_categories")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class ReminderCategory(Base):
    __tablename__ = 'reminder_categories'

    reminder_id = Column(Integer, ForeignKey('reminders.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)

    def __repr__(self):
        return f"<ReminderCategory(reminder_id={self.reminder_id}, category_id={self.category_id})>"


class UserCategory(Base):
    __tablename__ = 'user_categories'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)

    def __repr__(self):
        return f"<UserCategory(user_id={self.user_id}, category_id={self.category_id})>"


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)

def save_user(telegram_id, username):
    if get_user_by_telegram_id(telegram_id) is not None:
        return
    with SessionLocal() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            created_at=datetime.datetime.now()
        )
        session.add(user)
        session.commit()


def save_reminder(reminder):
    reminder.message = encryption.encrypt(reminder.message)
    with SessionLocal() as session:
        session.add(reminder)
        session.commit()


def get_user_by_username(username):
    with SessionLocal() as session:
        return session.query(User).filter(User.username == username).first()


def get_category_by_name(name):
    with SessionLocal() as session:
        return session.query(Category).filter(Category.name == name).first()


def get_all_user_reminders(user_id):
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        reminders = user.reminders

    for r in reminders:
        r.message = encryption.decrypt(r.message)

    return reminders


def get_user_tg_id_categories(tg_id):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == tg_id).first()
        categories = user.categories

    return categories


def get_valid_user_reminders(user_id):
    with SessionLocal() as session:
        reminders = session.query(Reminder).filter(
            and_(Reminder.user_id == user_id, Reminder.is_done == False)
        ).order_by(Reminder.reminder_time).all()

    for r in reminders:
        r.message = encryption.decrypt(r.message)

    return reminders


def get_valid_user_reminders_from_category(user_id, category_name):
    with SessionLocal() as session:
        reminders = session.query(Reminder).join(Reminder.categories).filter(
            and_(Reminder.user_id == user_id, Reminder.is_done == False, Category.name == category_name)
        ).order_by(Reminder.reminder_time).all()

    for r in reminders:
        r.message = encryption.decrypt(r.message)

    return reminders


def get_reminders_to_remind():
    with SessionLocal() as session:
        current_time = datetime.datetime.now()

        reminders = session.query(Reminder).filter(
            or_(and_(Reminder.reminder_time <= current_time, Reminder.is_done == False),
                and_(Reminder.reminder_time_delta <= current_time, Reminder.is_delta_done == False))).all()

    for r in reminders:
        r.message = encryption.decrypt(r.message)

    return reminders


def get_user_by_telegram_id(id):
    with SessionLocal() as session:
        return session.query(User).filter(User.telegram_id == id).first()


def init_db():
    # Создание таблиц
    Base.metadata.create_all(engine)


def main():
    init_db()

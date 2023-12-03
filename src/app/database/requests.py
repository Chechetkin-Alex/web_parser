from src.app.database.models import *
from sqlalchemy import select, delete
import logging


async def does_user_exist(user_id):
    async with async_session() as session:
        user_in_db = await session.scalar(select(Users).where(Users.tg_id == user_id))
        have_preferences = 0
        try:
            have_preferences = await session.scalar(select(Preferences).where(user_in_db[0].id == Preferences.user_id))
        except TypeError:
            pass
        return user_in_db, have_preferences


async def add_user(user_data):
    async with async_session() as session:
        try:
            session.add(Users(tg_id=user_data["tg_id"], chat_id=user_data["chat_id"], station=user_data["station"],
                              time_to_station=user_data["time_to_station"],
                              course=user_data["course"], group_num=user_data["group_num"]))
            await session.commit()
            return True
        except Exception as e:
            logging.error('Error: %s', exc_info=e)
            return False


async def add_preferences(user_tg_id, user_data):
    async with async_session() as session:
        try:
            user = await session.scalar(select(Users).where(Users.tg_id == user_tg_id))
            for i in range(6):
                lesson = user_data["first_lessons"][i]

                if lesson != -1:
                    session.add(Preferences(user_id=user.id, day=i + 1, first_lesson=lesson.split(" | ")[0]))
                else:
                    session.add(Preferences(user_id=user.id, day=i + 1, first_lesson="-1"))
            await session.commit()
            return True
        except Exception as e:
            logging.error('Error: %s', exc_info=e)
            return False


async def restart(user_tg_id):
    async with async_session() as session:
        try:
            user = await session.scalar(select(Users).where(Users.tg_id == user_tg_id))
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            logging.error('Error: %s', exc_info=e)
            return False


async def set_clients_for_today(today):
    async with async_session() as session:
        try:
            await session.query(WaitingList).delete()

            clients_preferences = await session.scalar(
                select(Preferences).where(Preferences.day == today, Preferences.first_lesson != "-1"))
            for client in clients_preferences:
                await session.add(WaitingList(chat_id=client.users.chat_id, time_to_write=client.first_lesson[:5]))
            await session.commit()
        except Exception as e:
            logging.error('Error: %s', exc_info=e)


async def get_clients_for_today():
    async with async_session() as session:
        try:
            res = []
            for client in await session.scalar(select(WaitingList)):
                res.append((client.chat_id, client.time_to_write))
            return res
        except Exception as e:
            logging.error('Error: %s', exc_info=e)
            return False


async def get_station_and_time_to_station(chat):
    async with async_session() as session:
        try:
            client = await session.scalar(select(Users).where(Users.chat_id == chat))
            return client.station, client.time_to_station
        except Exception as e:
            logging.error('Error: %s', exc_info=e)
            return False

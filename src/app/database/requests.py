from src.app.database.models import Users, Preferences, async_session
from sqlalchemy import select


async def does_user_exist(user_id):
    async with async_session() as session:
        user_query = await session.scalar(select(Users).where(Users.tg_id == user_id))
        return user_query


async def add_user(user_data):
    async with async_session() as session:
        try:
            session.add(Users(tg_id=user_data["tg_id"], station=user_data["station"],
                              time_to_station=user_data["time_to_station"],
                              course=user_data["course"], group_num=user_data["group_num"]))
            await session.commit()
            return True
        except:
            return False


async def add_preferences(user_data):
    async with async_session() as session:
        try:
            for lesson in user_data["removed_lessons"]:
                session.add(Preferences(useless_lesson=lesson))
            await session.commit()
            return True
        except:
            return False

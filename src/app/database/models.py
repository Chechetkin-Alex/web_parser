from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from src.config_reader import config

engine = create_async_engine(config.sqlalchemy_url.get_secret_value(), echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    station: Mapped[str] = mapped_column(String(50))
    time_to_station: Mapped[int]
    course: Mapped[int]
    group_num: Mapped[str] = mapped_column(String(15))

    preferences = relationship("Preferences", backref="users")


class Preferences(Base):
    __tablename__ = 'preferences'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    day: Mapped[int]
    first_lesson: Mapped[str] = mapped_column(String(250))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

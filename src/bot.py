import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config_reader import config
from app.database.models import async_main
from app.handlers import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.requests import *
from weather_parser import Weather
from trains_parser import Trains
import sys
import logging
from datetime import datetime, timedelta


async def main():
    await async_main()

    TOKEN = config.telegram_api_token.get_secret_value()
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    run_scheduler(bot)
    await dp.start_polling(bot)


def run_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(make_decision, "cron", hour=8, minute=30, args=(bot, scheduler))
    scheduler.start()


async def make_decision(bot, scheduler):
    await set_clients_for_today(datetime.now().weekday() + 1)
    will_it_rain = Weather().get_weather_around_mipt()
    if will_it_rain:
        for chat, timing in await get_clients_for_today():
            station, time_to_station = await get_station_and_time_to_station(chat)
            target_time = datetime.strptime(timing, "%H:%M") - timedelta(minutes=15) - timedelta(
                minutes=time_to_station) - timedelta(minutes=Trains().stations[station][1])
            scheduler.add_job(send_notification, "date",
                              run_time=datetime.now().replace(
                                  hour=target_time.hour, minute=target_time.minute, second=00),
                              args=(bot, chat, will_it_rain))


async def send_notification(bot, chat_id, current_time):
    await bot.send_message(text=f"<i>Внимание, {current_time} возможны осадки в виде фрикаделек!</i>\n"
                                "Не забудь захватить зонтик.", chat_id=chat_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

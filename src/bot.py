import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config_reader import config
from app.database.models import async_main
from app.handlers import router
import sys
import logging


async def main():
    await async_main()

    TOKEN = config.telegram_api_token.get_secret_value()
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

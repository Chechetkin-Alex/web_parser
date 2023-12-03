# Umbrella Reminder Bot

The Umbrella Reminder Bot is designed to solve the common problem of forgetting an umbrella when leaving home during rainy weather. This bot allows users to input the time it takes to reach the train station, and it will automatically monitor the weather conditions. Five minutes before the specified departure time, the bot will send a notification, reminding the user to grab an umbrella if necessary.

The primary aim is to assist users, particularly those heading to classes, in avoiding the inconvenience of getting caught in the rain without proper protection.

Before usage, install modeles from `requirements.txt`
```shell
pip install -r requirements.txt
```

And create `.env` in `src/` with structure like this:
```
YANDEX_TRAINS_API_KEY = ... (get on yandex.ru/dev/)
YANDEX_WEATHER_API_KEY = ... (get on yandex.ru/dev/)
TELEGRAM_API_TOKEN = ... (ask BotFather)
SQLALCHEMY_URL = sqlite+aiosqlite:///resources/db.sqlite3
```

Then run
```shell
python3 bot.py
```
**Enjoy!**

This project is made for educational purposes.

### Made by:
- *Chechetkin Alexander*
    - GitHub: *@Chechetkin-Alex*
    - Telegram: *@snakemanysss*

Autumn 2023

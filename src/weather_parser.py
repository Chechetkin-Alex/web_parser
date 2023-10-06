from dotenv import load_dotenv
import os
import requests


class Weather:
    url = "https://api.weather.yandex.ru/v2/informers?"
    novodachnaya_coord = (55.924457, 37.527858)

    def __init__(self):
        load_dotenv()  # loading environmental variables

    def get_weather(self, start_area):
        weather_in_start_area = self.get_weather_in_area(start_area)
        weather_in_novodachnaya = self.get_weather_in_area(self.novodachnaya_coord)

        return weather_in_start_area, weather_in_novodachnaya

    def get_weather_in_area(self, area):
        params = {
            "lat": area[0],
            "lon": area[1]
        }
        header = {'X-Yandex-API-Key': os.getenv("YANDEX_WEATHER_API_KEY")}
        response = requests.get(self.url, params=params, headers=header).json()

        ''' parse data in the morning! '''

        weather_with_day_time = {
            "morning": response["fact"]["condition"],
            "day": response["forecast"]["parts"][0]["condition"],
            "evening": response["forecast"]["parts"][1]["condition"]
        }

        return weather_with_day_time


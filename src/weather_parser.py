from config_reader import config
import requests


class Weather:
    url = "https://api.weather.yandex.ru/v2/informers?"
    mipt_coord = (55.924457, 37.527858)
    bad_weather = ("light-rain", "rain", "heavy-rain", "showers", "wet-snow",
                   "hail", "thunderstorm", "thunderstorm-with-rain", "thunderstorm-with-hail")

    def get_weather_around_mipt(self):
        params = {
            "lat": self.mipt_coord[0],
            "lon": self.mipt_coord[1]
        }
        header = {'X-Yandex-API-Key': config.yandex_weather_api_key.get_secret_value()}
        response = requests.get(self.url, params=params, headers=header).json()

        ''' parse data in the morning! '''

        weather_with_day_time = {
            "morning": response["fact"]["condition"],
            "day": response["forecast"]["parts"][0]["condition"],
            "evening": response["forecast"]["parts"][1]["condition"]
        }

        if weather_with_day_time["morning"] in self.bad_weather:
            return "утром"
        if weather_with_day_time["day"] in self.bad_weather:
            return "днём"
        if weather_with_day_time["evening"] in self.bad_weather:
            return "вечером"
        return 0


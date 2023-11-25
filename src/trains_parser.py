from config_reader import config
import requests
import datetime


class TrainsParser:
    soup = ""
    url = "https://api.rasp.yandex.net/v3.0/search/"
    trains = []
    delay = 0

    def __init__(self, delay):
        self.delay = delay

    def find_trains(self, from_station, to_station, date):
        params = {
            "apikey": config.yandex_trains_api_key.get_secret_value(),
            "from": from_station,
            "to": to_station,
            "limit": 200,
            "date": date
        }
        response = requests.get(self.url, params=params).json()

        for i in range(len(response["segments"])):
            title = response["segments"][i]["thread"]["transport_subtype"]["title"]
            departure = response["segments"][i]["departure"]
            arrival = response["segments"][i]["arrival"]

            ''' 
            get useful time type; 
            sorted by departure time 
            '''

            departure = datetime.datetime.fromisoformat(departure)
            arrival = datetime.datetime.fromisoformat(arrival)

            self.trains.append(
                {
                    "title": title,
                    "departure": departure,
                    "arrival": arrival
                }
            )

    def find_nearest_train(self, time):
        for train in self.trains:
            if (train["departure"] - time).total_seconds() >= self.delay:
                return train

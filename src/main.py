import datetime
from trains_parser import TrainsParser
from mipt_schedule_parser import MIPTSchedule
from weather_parser import Weather


def get_train():
    delay = 20 * 60
    stations = {
        "Beskudnikovo": "s9601805",
        "Novodachnaya": "s9601261"
    }
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    time = datetime.datetime.now(datetime.timezone.utc)  # convert into aware datetime

    route = TrainsParser(delay)
    route.find_trains(stations["Beskudnikovo"], stations["Novodachnaya"], date)
    train = route.find_nearest_train(time)


def get_schedule():
    schedule = MIPTSchedule(2, "Б05-221")
    schedule.download_schedule()
    # schedule.find_first_class(datetime.datetime.today().weekday() + 1)
    schedule.find_first_class(2)


def get_weather():
    beskudnikovo_coord = (55.882167, 37.567267)
    weather = Weather()
    print(weather.get_weather(beskudnikovo_coord))


get_weather()

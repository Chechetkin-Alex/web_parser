# import datetime
# from trains_parser import TrainsParser
from mipt_schedule_parser import MIPTSchedule
from weather_parser import Weather


# def get_train():
#     delay = 20 * 60  # in seconds
#     stations = {
#         "Beskudnikovo": "s9601805",
#         "Novodachnaya": "s9601261"
#     }
#     date = datetime.datetime.today().strftime('%Y-%m-%d')
#     time = datetime.datetime.now(datetime.timezone.utc)  # convert into aware datetime
#
#     route = TrainsParser(delay)
#     route.find_trains(stations["Beskudnikovo"], stations["Novodachnaya"], date)
#     train = route.find_nearest_train(time)


# def get_schedule():
#     schedule = MIPTSchedule()
#     schedule.set_course(2)
#     schedule.download_schedule()
#     print(schedule.get_all_groups())
    # schedule.find_first_class(datetime.datetime.today().weekday() + 1)
    # for i in range(8):
    #     print(schedule.find_first_subject(i))


def get_weather():
    beskudnikovo_coord = (55.882167, 37.567267)
    weather = Weather()
    print(weather.get_weather(beskudnikovo_coord))


get_weather()

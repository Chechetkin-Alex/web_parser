from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.trains_parser import TrainsParser

initial_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Погнали")]], resize_keyboard=True)

back_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True)

courses_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3"), KeyboardButton(text="4")],
              [KeyboardButton(text="Назад")]], resize_keyboard=True)


def groups_kb(groups_num):
    builder = ReplyKeyboardBuilder()
    for group in groups_num:
        builder.add(KeyboardButton(text=group))
    return builder.as_markup(resize_keyboard=True)


def station_kb():
    stations = []
    for station in TrainsParser().stations.keys():
        stations.append([KeyboardButton(text=station)])
    stations.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=stations, resize_keyboard=True)


validation_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="-Сова, подтверди! -Подтверждаю.")],
    [KeyboardButton(text="Нет, ошибка в станции")],
    [KeyboardButton(text="Нет, ошибка во времени")],
    [KeyboardButton(text="Нет, ошибка в номере группы")],
    [KeyboardButton(text="Назад")]
])


def lessons_kb(lessons):
    subjects = []
    for subject in lessons:
        if subject != -1:
            subjects.append([KeyboardButton(text=subject)])
    subjects.append([KeyboardButton(text="undo")])
    subjects.append([KeyboardButton(text="Подтвердить")])
    return ReplyKeyboardMarkup(keyboard=subjects, resize_keyboard=True)


periods_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="1")],
    [KeyboardButton(text="2")],
    [KeyboardButton(text="1.5")],
    [KeyboardButton(text="0.5")]
])

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.trains_parser import Trains

initial_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Погнали")]], resize_keyboard=True)

back_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True)

courses_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3"), KeyboardButton(text="4")],
              [KeyboardButton(text="Назад")]], resize_keyboard=True)


def groups_kb(groups_num):
    sub_groups = []
    groups = []
    pos = 0
    for group in groups_num:
        if pos < 5:
            sub_groups.append(KeyboardButton(text=group))
            pos += 1
        else:
            pos = 0
            groups.append(sub_groups)
            sub_groups = []
    return ReplyKeyboardMarkup(keyboard=groups, resize_keyboard=True)


def station_kb():
    stations = []
    for station in Trains().stations.keys():
        stations.append([KeyboardButton(text=station)])
    stations.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=stations, resize_keyboard=True)


validation_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="-Филин, подтверди! -Подтверждаю.")],
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

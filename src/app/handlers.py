import re
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold, Italic
from aiogram.utils.markdown import hide_link
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.app.database.requests import *
from src.trains_parser import TrainsParser as Train
from src.mipt_schedule_parser import MIPTSchedule
import src.app.keyboards as kb
import asyncio

router = Router()


class Registration(StatesGroup):
    get_started = State()
    station = State()
    time_to_station = State()
    group_num = State()
    validate = State()


class Choosing(StatesGroup):
    subjects = State()
    period = State()


@router.message(Command("start"))
async def cmd_start_handler(message: Message, state: FSMContext):
    is_registered = await does_user_exist(message.from_user.id)
    if not is_registered:
        await state.set_state(Registration.get_started)
        await message.answer(f"{hide_link('https://images.stopgame.ru/news/2017/11/25/bz9eZgZ0j.jpg')}"
                             f"- Для чего я создан?\n"
                             f"- Чтоб напоминать мне взять зонтик.\n"
                             f"- Боже мой...")
        await asyncio.sleep(0.01)  # todo 1
        await message.answer("А если серьезно, то с автором данного бота часто "
                             "случались приключения, когда он, выходя из дома, по тем или иным "
                             "причинам забывал взять зонтик, а ходить осенью в мокрой ветровке "
                             "не хотелось. Я же создан решить эту проблему! В меня можно забить "
                             "время, которое тебе идти до станции, саму станцию, а дальше я буду "
                             "автоматически мониторить погоду и отправлять тебе уведомление аккурат "
                             "за 5 минут до выхода. Естественно с расчетом на то, что ты идешь на пары. "
                             "Список пар, которые ты посещаешь, далее можно будет указать.\n"
                             "Ну-с, давай продолжим!", reply_markup=kb.initial_kb)
    else:
        await message.answer(
            f'Давненько не виделись, {message.from_user.full_name}!\nВсе в силе или нужно что-то поменять?',
            reply_markup=ReplyKeyboardRemove())  # todo


@router.message(Registration.get_started)
async def get_station(message: Message, state: FSMContext):
    await state.set_state(Registration.station)
    await state.update_data(tg_id=message.from_user.id)
    await message.answer("Ты всегда можешь вернуться назад написав в чат <b>Назад</b> "
                         "или нажав соответствующую кнопку.",
                         reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    await message.answer("Выбери станцию из уже доступных:", reply_markup=kb.station_kb())


@router.message(Registration.station)
async def get_station(message: Message, state: FSMContext):
    if message.text.lower() == "назад":
        await state.set_state(Registration.get_started)
        await message.answer("А если серьезно, то с автором данного бота часто "
                             "случались приключения, когда он, выходя из дома, по тем или иным "
                             "причинам забывал взять зонтик, а ходить осенью в мокрой ветровке "
                             "не хотелось. Я же создан решить эту проблему! В меня можно забить "
                             "время, которое тебе идти до станции, саму станцию, а дальше я буду "
                             "автоматически мониторить погоду и отправлять тебе уведомление аккурат "
                             "за 5 минут до выхода. Естественно с расчетом на то, что ты идешь на пары. "
                             "Список пар, которые ты посещаешь, далее можно будет указать.\n"
                             "Ну-с, давай продолжим!", reply_markup=kb.initial_kb)
        return
    if message.text not in kb.TrainsParser().stations.keys():
        await message.answer("Я такую пока не знаю(\n"
                             "Лучше выбери из моего списка")
        return

    await state.update_data(station=message.text)
    await state.set_state(Registration.time_to_station)
    await message.answer("Отлично! А сколько тебе <b>минут</b> до неё идти?",
                         reply_markup=kb.back_kb, parse_mode=ParseMode.HTML)


@router.message(Registration.time_to_station)
async def get_station(message: Message, state: FSMContext):
    answer = message.text
    if answer.lower() == "назад":
        await state.set_state(Registration.station)
        await message.answer("Выбери станцию из уже доступных:", reply_markup=kb.station_kb())
        return
    if not answer.isdigit() or int(answer) <= 0 or int(answer) > 100:
        await message.answer("Не нравятся мне эти данные, попробуй ввести нормально")
        return

    await state.update_data(time_to_station=int(message.text))
    await state.set_state(Registration.group_num)
    await message.answer("А ещё, какой у тебя курс и номер группы?\n"
                         "В формате <b>?, Б??-???</b>\n"
                         "Например: <b>2, Б05-211</b>",
                         reply_markup=kb.back_kb,
                         parse_mode=ParseMode.HTML)


@router.message(Registration.group_num)
async def get_station(message: Message, state: FSMContext):
    if message.text.lower() == "назад":
        await state.set_state(Registration.time_to_station)
        await message.answer("Отлично! А сколько тебе <b>минут</b> до неё идти?",
                             reply_markup=kb.back_kb, parse_mode=ParseMode.HTML)
        return
    if not re.compile(r"\d, [А-Я]\d{2}-\d{3}").match(message.text.upper()):
        await message.answer("Начальника, переделывай :(")
        return

    course, group_num = message.text.split(", ")
    await state.update_data(course=course, group_num=group_num)
    await state.set_state(Registration.validate)
    user_data = await state.get_data()
    await message.answer(f"<i>Сверяем данные</i>:\n\n"
                         f"<b>Имя</b>: {message.from_user.full_name} ,\n"
                         f"<b>Ближайшая станция</b>: {user_data['station']} ,\n"
                         f"<b>Сколько топать</b>: {user_data['time_to_station']} мин,\n"
                         f"<b>Курс и номер группы</b>: {user_data['course']}, {user_data['group_num']} ,\n"
                         f"<del>Номер военного биле</del> Кхм, пожалуй, достаточно :D", parse_mode=ParseMode.HTML)
    await message.answer(f"Все верно?", reply_markup=kb.validation_kb)


@router.message(Registration.validate)
async def validate(message: Message, state: FSMContext):
    if message.text == "Нет, ошибка в станции":
        await state.set_state(Registration.station)
        return
    if message.text == "Нет, ошибка во времени":
        await state.set_state(Registration.time_to_station)
        return
    if message.text == "Нет, ошибка в номере курса или группы":
        await state.set_state(Registration.group_num)
        return

    user_data = await state.get_data()
    if await add_user(user_data):
        await message.answer("Всё классно, я тебе запомнил)", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Error 404 я сломался :((\n Напиши админу @snakemanysss")
        await state.clear()
        return
    await message.answer(f"Запускаю поиск по предметам...")
    schedule = MIPTSchedule(user_data["course"], user_data["group_num"])
    await state.update_data(schedule=schedule)
    await schedule.download_schedule()
    first_lessons = []
    answer = f"Вот, какие предметы тебя ждут по утрам:\n"
    for day in range(1, 8):
        first_lessons.append(await schedule.find_first_subject(day))
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for i in range(0, 7):
        if first_lessons[i] != -1:
            answer += f"{days[i]}: {first_lessons[i]}\n"
    await message.answer(answer + "<b>На какие из них забиваешь?)</b>\n"
                                  "Если случайно нажал лишнее, нажми <i>undo</i>",
                         parse_mode=ParseMode.HTML,
                         reply_markup=kb.lessons_kb(first_lessons))
    await state.update_data(removed_lessons=[], first_lessons=first_lessons)
    await state.set_state(Choosing.subjects)


@router.message(Choosing.subjects)
async def choosing_subjects(message: Message, state: FSMContext):
    if message.text == "Подтвердить":
        await message.answer("Отлично! Вот твой список:")

    user_data = await state.get_data()
    user_data["removed_lessons"].append(message.text)
    await state.update_data(removed_lessons=user_data["removed_lessons"])
    await message.answer("А какая продолжительность <b>в парах</b> у этого предмета?",
                         parse_mode=ParseMode.HTML,
                         reply_markup=kb.periods_kb)
    await state.set_state(Choosing.period)


@router.message(Choosing.period)
async def choosig_period(message: Message, state: FSMContext):

    user_data = await state.get_data()
    period = int(message.text * 2)  # todo check int
    answer = f"<b>Убрано:</b>\n"
    for subject in user_data["removed_lessons"]:
        answer += f"{subject},\n"
    answer += f"\n<b>В какие дни что остаётся:</b>\n"
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for i in range(0, 7):
        if user_data["first_lessons"][i] == -1:
            continue
        if user_data["first_lessons"][i] not in user_data["removed_lessons"]:
            answer += f"{days[i]}: {user_data['first_lessons'][i]}\n"
        else:
            user_data["schedule"].optional_subjects[user_data["first_lessons"][i]] = period
            subject = user_data['schedule'].find_first_subject(i)
            answer += f"{days[i]}: {subject}\n"
            user_data["first_lessons"].remove(subject)  # todo delete several lessons
            await state.update_data(first_lessons=user_data["first_lessons"])
    await state.set_state(Choosing.subjects)
    await message.answer(answer, parse_mode=ParseMode.HTML, reply_markup=kb.lessons_kb(user_data["first_lessons"]))


@router.message(Command("help"))
async def cmd_help(message: Message):
    content = Text("Hello, \n\n", Bold(message.from_user.full_name), "!")  # todo
    await message.answer(**content.as_kwargs())

# @router.message()
# async def echo_handler(message: Message) -> None:
#     try:
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         await message.answer("Nice try!")

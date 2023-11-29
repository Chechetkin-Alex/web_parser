import re
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold
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
    course = State()
    group_num = State()
    validate = State()


class Choosing(StatesGroup):
    subjects = State()
    period = State()
    complete = State()


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
    await state.set_state(Registration.course)
    await message.answer("Выбери свой курс\n",
                         reply_markup=kb.courses_kb,
                         parse_mode=ParseMode.HTML)


@router.message(Registration.course)
async def get_course(message: Message, state: FSMContext):
    if message.text.lower() == "назад":
        await state.set_state(Registration.time_to_station)
        await message.answer("Отлично! А сколько тебе <b>минут</b> до неё идти?",
                             reply_markup=kb.back_kb, parse_mode=ParseMode.HTML)
        return
    try:
        if int(message.text) not in range(1, 5):
            await message.answer("Какой-какой?")
            return
    except ValueError:
        await message.answer("??")
        return

    await state.update_data(course=int(message.text))
    schedule = MIPTSchedule()
    schedule.set_course(int(message.text))
    schedule.download_schedule()
    await state.update_data(schedule=schedule)
    await message.answer("Выбери свою группу", reply_markup=kb.groups_kb(schedule.get_all_groups()))
    await state.set_state(Registration.group_num)


@router.message(Registration.group_num)
async def get_station(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text.lower() == "назад":
        await state.set_state(Registration.time_to_station)
        await message.answer("Выбери свою группу", reply_markup=kb.groups_kb(user_data["schedule"].get_all_groups()))
        return
    if not re.compile(r"[А-Я]\d{2}-\d{3}").match(message.text.upper()) or \
            message.text not in user_data["schedule"].get_all_groups():
        await message.answer("Начальника, переделывай :(")
        return

    user_data["schedule"].set_group(message.text)
    await state.update_data(group_num=message.text, schedule=user_data["schedule"])
    await state.set_state(Registration.validate)

    await message.answer(f"<i>Сверяем данные</i>:\n\n"
                         f"<b>Имя</b>: {message.from_user.full_name} ,\n"
                         f"<b>Ближайшая станция</b>: {user_data['station']} ,\n"
                         f"<b>Сколько топать</b>: {user_data['time_to_station']} мин,\n"
                         f"<b>Курс и номер группы</b>: {user_data['course']}, {message.text} ,\n"
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
        await state.set_state(Registration.course)
        return

    user_data = await state.get_data()
    if await add_user(user_data):
        await message.answer("Всё классно, я тебе запомнил)", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Error 404 я сломался :((\nНапиши админу @snakemanysss")
        await state.clear()
        return

    await message.answer(f"Запускаю поиск по предметам...")
    schedule = user_data["schedule"]
    first_lessons = []
    answer = f"<b>Вот, какие предметы тебя ждут по утрам:</b>\n"
    for day in range(1, 8):
        first_lessons.append(schedule.find_first_subject(day))
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for i in range(0, 7):
        if first_lessons[i] != -1:
            answer += f"<u>{days[i]}</u>: {first_lessons[i]}\n"
    await message.answer(answer + "\n<b>На какие из них забиваешь?)</b>",
                         parse_mode=ParseMode.HTML,
                         reply_markup=kb.lessons_kb(first_lessons))
    await state.update_data(removed_lessons=[], first_lessons=first_lessons)
    await state.set_state(Choosing.subjects)


@router.message(Choosing.subjects)
async def choosing_subjects(message: Message, state: FSMContext):
    user_data = await state.get_data()

    if message.text == "Подтвердить":
        answer = "\n"
        if len(user_data["removed_lessons"]) > 0:
            for subject in user_data["removed_lessons"][:-1]:
                answer += f"{subject},\n"
            answer += f"{user_data['removed_lessons'][-1]}.\n"
        if answer == "\n":
            await message.answer("<u>Не забиваешь на пары, красава</u> 😉",
                                 parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("<u>Отлично! Вот финальный список:</u>" + answer,
                                 parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        await message.answer("Заношу в базу данных...")

        if await add_preferences(message.from_user.id, user_data):
            await message.answer("Done")
        else:
            await message.answer("Error 404 я сломался :((\nНапиши админу @snakemanysss")
            await state.clear()
            return
        await state.set_state(Choosing.complete)
        return

    if message.text == "undo":
        if len(user_data["removed_lessons"]) > 0:
            user_data["first_lessons"].pop(user_data["removed_lessons"][-1][0])
            user_data["first_lessons"].insert(user_data["removed_lessons"][-1][0],
                                              user_data["removed_lessons"][-1][1])
            user_data["removed_lessons"].pop()
            await state.update_data(removed_lessons=user_data["removed_lessons"],
                                    first_lessons=user_data["first_lessons"])

            answer = f"<b>Убрано:</b>\n"
            answer += f"\n<b>В какие дни что остаётся:</b>\n"
            days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            for i in range(0, 7):
                if user_data["first_lessons"][i] == -1:
                    continue
                answer += f"<u>{days[i]}</u>: {user_data['first_lessons'][i]}\n"

            await message.answer(answer, parse_mode=ParseMode.HTML,
                                 reply_markup=kb.lessons_kb(user_data["first_lessons"]))
        else:
            await message.answer("А что мне отменить..")

        return

    not_found = True
    for i, subject in enumerate(user_data["first_lessons"]):
        if isinstance(subject, str) and message.text[:100] in subject:
            if message.text not in user_data["removed_lessons"]:
                user_data["removed_lessons"].append((i, subject))
                await state.update_data(removed_lessons=user_data["removed_lessons"])
                not_found = False
            else:
                await message.answer("Уже было")
                return

    if not_found:
        await message.answer("Не знаю такого")
        return

    await message.answer("А какая продолжительность <b>в парах</b> у этого предмета?",
                         parse_mode=ParseMode.HTML,
                         reply_markup=kb.periods_kb)
    await state.set_state(Choosing.period)


@router.message(Choosing.period)
async def choosing_period(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        period = int(float(message.text) * 2)
    except ValueError as e:
        logging.error('Error: %s', exc_info=e)
        await message.answer("Число, пожалуйста")
        return
    answer = f"<b>Убрано:</b>\n"
    for subject in user_data["removed_lessons"][:-1]:
        answer += f"{subject[1]},\n"
    answer += f"{user_data['removed_lessons'][-1][1]}.\n"
    # todo handle all subjects a day deleted
    answer += f"\n<b>В какие дни что остаётся:</b>\n"
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for i in range(0, 7):
        if user_data["first_lessons"][i] == -1:
            continue
        if all(user_data["first_lessons"][i] not in subject[1] for subject in user_data["removed_lessons"]):
            answer += f"<u>{days[i]}</u>: {user_data['first_lessons'][i]}\n"
        else:
            user_data["schedule"].set_optional_subjects(user_data["first_lessons"][i], period)
            await state.update_data(schedule=user_data["schedule"])
            new_subject = user_data["schedule"].find_first_subject(i + 1)
            user_data["first_lessons"].insert(i, new_subject)
            user_data["first_lessons"].remove(user_data["removed_lessons"][-1][1])
            answer += f"<u>{days[i]}</u>: {new_subject}\n"
            await state.update_data(first_lessons=user_data["first_lessons"])

    await state.set_state(Choosing.subjects)
    await message.answer(answer, parse_mode=ParseMode.HTML, reply_markup=kb.lessons_kb(user_data["first_lessons"]))


@router.message(Choosing.complete)
async def accomplished(message: Message, state: FSMContext):
    pass


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

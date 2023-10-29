from typing import Callable
from enum import Enum
import telebot
from telebot import types
from arrow import utcnow
from io import BytesIO


# Импорт моделей и функций из других модулей
from bd.model import Message, Session
from reports import reports, get_reports
from util import format_message_list4


# Определить состояния сессии
class State(str, Enum):
    INIT = "INIT"  # Начальное состояние сеанса
    MENU = "MENU"  # Меню с выбором отчета
    INPUT = "INPUT"  # Ввод данных для отчета
    REPLY = "REPLY"  # Ответ на вопросы отчета
    READY = "READY"  # Готовность отчета к отправке


# Обработчик входящие сообщения
async def handle_message(bot: telebot.TeleBot, message: Message, session: Session):
    # Определить список стартовых команд
    start = ["Menu", "/start", "Меню"]
    # Проверьте, является ли сообщение командой запуска.
    if message.text in start:
        # Сброс состояния сессии и комнаты
        session.state = State.INIT
        session.room = "0"
        session.update(room=session.room, state=session.state)
    # Определим функцию для следующего шага
    next = lambda: handle_message(bot, message, session)
    try:
        # Вызов соответствующего обработчика состояния на основе состояния сессии
        await states[session.state](bot, message, session, next)
    except Exception as ex:
        print(ex)
        # raise ex
        # Обработка исключений и уведомление пользователя
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_address = types.KeyboardButton("Меню")
        markup.add(btn_address)
        await bot.send_message(message.chat_id, "Произошла ошибка", reply_markup=markup)
        session.state = State.INIT
        next()


# Обработка состояния INIT (начальное состояние)
async def handle_init_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):
    # Создайте меню «Пуск» с опциями отчета
    start_menu = types.InlineKeyboardMarkup(row_width=2)
    for name, report in get_reports(session).items():
        # print(name)
        button = types.InlineKeyboardButton(report.name, callback_data=name)
        start_menu.add(button)
    # Отправьте приветственное сообщение через меню «Пуск»
    await bot.send_message(message.chat_id, "Привет", reply_markup=start_menu)
    # Инициализируем параметры сессии
    room = session.room
    session.params = {"inputs": {room: {}}}
    # Переход в состояние МЕНЮ
    session.state = State.MENU

    # Обновляем состояние сессии и params
    session.update(params=session.params, state=session.state)


# Обработка состояния MENU (состояние выбора опции в меню)
async def handle_menu_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):
    # Установить выбранный отчет в параметрах сессии
    session.params["report"] = message.text

    # Переход в состояние INPUT
    session.state = State.INPUT

    # Обновляем состояние сессии
    session.update(state=session.state, params=session.params)

    await next()


# Обработка состояния INPUT(Ввод данных для отчета)
async def handle_input_state(bot, message, session, next):
    report = reports[session.params["report"]]
    # Перебираем поля ввода отчета
    for name, Input in report.get_inputs(session).items():
        # print(name)
        room = session.room
        if name not in session.params["inputs"][room]:
            session.params["input"] = name
            session.update(params=session.params)
            input = Input()
            # Обработка различных типов ввода
            if input.type == "SELECT":
                # Создаем кнопку для каждой опции
                markup = types.InlineKeyboardMarkup(row_width=2)
                options = input.get_options(session)  # [{}, {}, {}, ...]
                for option in options:  # [({}, 0), ({}, 1), ({}, 2)]
                    button = types.InlineKeyboardButton(
                        option["name"], callback_data=option["id"]
                    )
                    markup.add(button)
            if input.type == "LOCATION":
                # Обработка ввода LOCATION (местоположения)
                options = input.get_options(session)  # [{}, {}, {}, ...]
                print(options[0]["name"])
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn_address = types.KeyboardButton(
                    options[0]["name"], request_location=True
                )
                markup.add(btn_address)
            if input.type == "PHOTO":
                # Обработка ввода фотографии
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn_address = types.KeyboardButton("Меню")
                markup.add(btn_address)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            if input.type == "FILE":
                # Обработка ввода файла
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn_address = types.KeyboardButton("Меню")
                markup.add(btn_address)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            if input.type == "MESSAGE":
                # Удаляем предыдущее сообщение и отправляем новое сообщение с клавиатурой
                await bot.delete_message(message.chat_id, message.message_id)
                await bot.send_message(message.chat_id, input.desc)
            if input.type == "SELECT":
                # Удаляем предыдущее сообщение и отправляем новое сообщение с клавиатурой
                await bot.delete_message(message.chat_id, message.message_id)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            if input.type == "LOCATION":
                # Удаляем предыдущее сообщение и отправляем новое сообщение с клавиатурой
                await bot.delete_message(message.chat_id, message.message_id)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            session.state = State.REPLY
            session.update(state=session.state)
            # session.save()

            return
    # Переход в состояние READY (Обработка готовности отчета)
    session.state = State.READY

    # Обновляем состояние сессии
    session.update(state=session.state)
    await next()


# Обработка состояния REPLY
async def handle_reply_state(bot, message, session, next):
    input_name = session.params["input"]
    room = session.room
    # Обработка команды "open" для перехода в следующую комнату
    if message.text == "open":
        session.room = str(int(session.room) + 1)
        session.params["inputs"][session.room] = {}
        session.update(params=session.params, room=session.room)
    # Создайте новое поле ввода в текущей комнате, если оно не существует
    if str(room) not in session.params["inputs"]:
        session.params["inputs"][str(room)] = {}
        session.update(params=session.params)
    # Сохраняйте введенные пользователем данные в зависимости от
    # типа сообщения (текст, местоположение, фотография, документ)
    session.params["inputs"][str(room)][input_name] = message.text
    session.update(params=session.params)
    # Обработка локации
    if message.location:
        session.params["inputs"][str(room)][input_name] = (
            utcnow().now().to("Etc/GMT-3").isoformat()
        )
        session.params["inputs"][str(room)][input_name] = {}
        session.params["inputs"][str(room)][input_name]["data"] = (
            utcnow().now().to("Etc/GMT-3").isoformat()
        )
        session.params["inputs"][str(room)][input_name][
            "lat"
        ] = message.location.latitude
        session.params["inputs"][str(room)][input_name][
            "lon"
        ] = message.location.longitude
        session.update(params=session.params)
 
    if message.photo:
        session.params["inputs"][str(room)][input_name] = {}
        session.params["inputs"][str(room)][input_name]["photo"] = message.photo[
            -1
        ].file_id
        session.update(params=session.params)
    # Обработка файла
    if message.document:
        # print(1)
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        # print(downloaded_file)

        # src = message.document.file_name
        # with open(src, "wb") as new_file:
        #     new_file.write(downloaded_file)
        # print(message.document.file_name)
        session.params["inputs"][str(room)][input_name] = downloaded_file
        # str(
        #     message.document.file_name
        # )

    # Переход в состояние INPUT (Обработка ввода данных)
    session.state = State.INPUT
    session.update(state=session.state)
    # session.save()
    await next()


# Обработка состояния READY
async def handle_ready_state(bot, message, session, next):
    # Получаем выбранный отчет из сессии
    report = reports[session.params["report"]]

    # Генерируем результат на основе выбранного отчета
    result = report.generate(session)

    # Если тип отчета - изображение
    if report.mime == "image":
        # Если есть файлы изображений, отправляем их
        if len(result[0]) > 0:
            for k, v in result[0].items():
                file_id = v
                await bot.send_photo(message.chat_id, file_id)

                # Форматируем и отправляем сообщения из списка результатов
                messages = format_message_list4(result[1])
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]
        else:
            # Если нет файлов изображений, только отправляем сообщения
            messages = format_message_list4(result[1])
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]
    if report.mime == "image_bytes":
        # Получение изображения
        image_bytes = result[1]
        print(image_bytes)

        # # Отправка изображения как фото
        await bot.send_photo(
            message.chat_id,
            photo=image_bytes,
        )
        # Отправляем сообщения
        messages = format_message_list4(result[0])
        [
            await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
            for m in messages
        ]
    else:
        # Если нет файлов изображений, только отправляем сообщения
        messages = format_message_list4(result)
        [
            await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
            for m in messages
        ]
    # Переход в состояние INPUT(Обработка начального состояния)
    session.state = State.INIT

    # Создаем клавиатуру с кнопкой "Меню"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_address = types.KeyboardButton("Меню")
    markup.add(btn_address)

    # Удаляем сообщение о результате и отправляем приветственное сообщение с клавиатурой
    await bot.delete_message(message.chat_id, message.message_id)
    await bot.send_message(message.chat_id, "Привет", reply_markup=markup)

    # Обновляем состояние сессии
    session.update(state=session.state)


states = {
    State.INIT: handle_init_state,  # Обработка начального состояния
    State.MENU: handle_menu_state,  # Обработка меню с выбором отчета
    State.INPUT: handle_input_state,  # Обработка ввода данных
    State.REPLY: handle_reply_state,  # Обработка ответов на вопросы
    State.READY: handle_ready_state,  # Обработка готовности отчета
}

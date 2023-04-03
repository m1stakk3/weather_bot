import json
import telebot
import random
from db.db import DB
from telebot import types
from methods import Weather
from os import path

# --------------------- CONFIG BLOCK ------------------------------------
CONFIG = json.load(open("config.json", "r", encoding="utf-8"))
YANDEX_API = CONFIG['yandex']
bot = telebot.TeleBot(CONFIG['telegram'])
db_path = path.normpath(CONFIG['database'])
# --------------------- CONSTANTS ----------------------------------------
EMOJIS_LIST = ['☔', '☁', '☀', '🌧', '⛅', '🌀', '🌨', '⛈', '🌩', '🌥', '🌦', '❄']
# -----------------------------------------------------------------------


@bot.message_handler(commands=['start', 'info'])
def welcome(message):
    # старт бота, запись данных о пользователе в БД
    if message.text == '/start':
        user_name = message.from_user.first_name
        bot.send_message(message.chat.id,
                         random.choice(EMOJIS_LIST) + f' Добро пожаловать {user_name}, я погодный бот!',
                         reply_markup=types.ReplyKeyboardRemove())
        if len(DB(db_path).return_query("SELECT user FROM data WHERE user='{}'".format(message.from_user.id))) == 0:
            DB(db_path).query("INSERT INTO data (user) VALUES ('{}')".format(message.from_user.id))
            bot.send_message(message.chat.id, "🤖: Укажите ваш город")
    if message.text == '/info':
        bot.send_message(message.chat.id, "🤖: Если у вас пропали кнопки для смены города, то введите в чат сообщение\n"
                                          "Сменить город")


@bot.message_handler(content_types=['text'])
def remember_city(message):
    BUTTONS = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # при первом запуске запоминается город пользователя
    if DB(db_path).return_query("SELECT city FROM data WHERE user='{}'".format(message.from_user.id))[0][0] is None:
        city = message.text.title()
        DB(db_path).query("UPDATE data SET city='{}' WHERE user='{}'".format(city, message.from_user.id))
        BUTTONS.add(types.KeyboardButton(f"Погода на 3 часа"), types.KeyboardButton("Сменить город"))
        bot.send_message(message.chat.id, "📍 Ваш город {}".format(city), reply_markup=BUTTONS)
        weather = Weather(city, YANDEX_API)
        bot.send_message(message.chat.id, weather.now())
        del weather
    else:
        if message.text == "Сменить город":
            bot.send_message(message.chat.id, "🤖: Введите название города", reply_markup=types.ReplyKeyboardRemove())
            # смена города, передача управления другому хендлеру
            bot.register_next_step_handler(message, new_city)
        elif message.text == "Погода на 3 часа":
            city = DB(db_path).return_query("SELECT city FROM data WHERE user='{}'".format(message.from_user.id))
            weather = Weather(city, YANDEX_API)
            bot.send_message(message.chat.id, weather.next_six_hours())
            del weather


def new_city(message):
    # перехватывает управление и устанвливает новый город, возвращает новые кнопки
    city = message.text
    DB(db_path).query("UPDATE data SET city='{}' WHERE user='{}'".format(city, message.from_user.id))
    BUTTONS = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    BUTTONS.add(types.KeyboardButton(f"Погода на 3 часа"), types.KeyboardButton("Сменить город"))
    bot.send_message(message.chat.id, "📍 Ваш город {}".format(city), reply_markup=BUTTONS)
    weather = Weather(city, YANDEX_API)
    bot.send_message(message.chat.id, weather.now())
    del weather


bot.infinity_polling()

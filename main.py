import json
import sqlite3
from string import Template
from urllib.parse import quote_plus
from urllib.request import urlopen
import telebot
from telebot import types

from util import *

bot = telebot.TeleBot(telegram_api_key_string)


@bot.message_handler(commands=["start"])
def begin(message, text=welcome_string):
    keyboard = types.ReplyKeyboardMarkup(row_width=3)

    add_item_button = types.KeyboardButton(add_item_button_string)
    show_items_button = types.KeyboardButton(show_items_button_string)
    calculate_items_button = types.KeyboardButton(calculate_items_button_string)
    remove_item_button = types.KeyboardButton(remove_item_button_string)
    clear_items_button = types.KeyboardButton(clear_items_button_string)
    finish_button = types.KeyboardButton(finish_button_string)
    show_weather_button = types.KeyboardButton(show_weather_button_string)
    analyze_stock_button = types.KeyboardButton(analyze_stock_button_string)

    keyboard.add(add_item_button, show_items_button, calculate_items_button)
    keyboard.add(remove_item_button, clear_items_button, finish_button)
    keyboard.add(show_weather_button, analyze_stock_button)

    msg = bot.send_message(message.from_user.id, text=text, reply_markup=keyboard)

    bot.register_next_step_handler(msg, answer)

    cursor = sqlite3.connect(list_bd_key_string).cursor()

    try:
        check = "CREATE TABLE \"list\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"item\" TEXT, PRIMARY KEY (\"ID\"))"
        cursor.execute(check)
    except:
        pass


def add_item(message):
    text = message.text
    text = text.split()
    try:
        float(text[-1])
    except:
        begin(message, "Введи цену последней!")
        return

    with sqlite3.connect(list_bd_key_string) as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO list (user_id, item) VALUES (?, ?)", (message.from_user.id, message.text))
        connection.commit()
    begin(message, added_string + help_string)


def show_list(message):
    with sqlite3.connect(list_bd_key_string) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT item FROM list WHERE user_id=={}".format(message.from_user.id))
        data = cursor.fetchall()
        data_list = []
        amount = 0
        for item in list(data):
            data_list.append(str(amount + 1) + ". " + item[0] + "\n")
            amount += 1
        data = "".join(data_list)
        bot.send_message(message.chat.id, "Товаров: " + str(amount))
        bot.send_message(message.chat.id, data)
        begin(message, help_string)


def count(message):
    with sqlite3.connect(list_bd_key_string) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT item FROM list WHERE user_id=={}".format(message.from_user.id))
        data = cursor.fetchall()
        amount = 0
        for item in list(data):
            item = item[0].split()
            amount += float(item[-1])
        bot.send_message(message.chat.id, "Итого набрано товаров на сумму: " + str(amount))
        begin(message, help_string)


def delete_item_start(message):
    to_delete_list = types.ReplyKeyboardMarkup(row_width=3)
    with sqlite3.connect(list_bd_key_string) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT item FROM list WHERE user_id=={}".format(message.from_user.id))
        data = cursor.fetchall()
        for item in list(data):
            to_delete_list.add(types.KeyboardButton(item[0]))
        if len(list(data)) == 0:
            begin(message, list_already_empty_string)
            return
        message = bot.send_message(message.from_user.id, text="Какой товар убрать?", reply_markup=to_delete_list)
        bot.register_next_step_handler(message, delete_item_end)


def delete_item_end(message):
    with sqlite3.connect(list_bd_key_string) as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM list WHERE user_id==? AND item==?", (message.from_user.id, message.text))
        connection.commit()
        begin(message, removed_string + help_string)


def clear_list(msg):
    with sqlite3.connect(list_bd_key_string) as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM list WHERE user_id=={}".format(msg.from_user.id))
        connection.commit()
    begin(msg, cleared_string + help_string)


def evaluate_json(json_data):
    temp = json_data["main"]["temp"]
    feels_like = json_data["main"]["feels_like"]
    return "Нынешняя: " + str(temp) + "С°. Ощущается как: " + str(feels_like) + "C°."


def get_weather(message):
    try:
        interpolated = Template(weathermap_query_string).substitute(city=quote_plus(message.text),
                                                                    units=default_units_key_string,
                                                                    lang=default_lang_key_string,
                                                                    api=weathermap_api_key_string)
        response = urlopen(interpolated)
        data = json.loads(response.read())
        evaluated = evaluate_json(data)
        begin(message, str(evaluated))
    except:
        begin(message, weather_error_string)


def analyze_stock(message):
    begin(message, "work in progress")


def answer(message):
    if message.text == add_item_button_string:
        item = bot.send_message(message.chat.id, add_item_example_string)
        bot.register_next_step_handler(item, add_item)
    elif message.text == show_items_button_string:
        try:
            show_list(message)
        except:
            bot.send_message(message.chat.id, list_empty_string)
            begin(message, begin_string)
    elif message.text == calculate_items_button_string:
        try:
            count(message)
        except:
            bot.send_message(message.chat.id, list_empty_string)
            begin(message, begin_string)
    elif message.text == remove_item_button_string:
        try:
            delete_item_start(message)
        except:
            bot.send_message(message.chat.id, list_already_empty_string)
            begin(message, begin_string)
    elif message.text == clear_items_button_string:
        try:
            clear_list(message)
        except:
            bot.send_message(message.chat.id, list_already_empty_string)
            begin(message, begin_string)
    elif message.text == show_weather_button_string:
        city = bot.send_message(message.chat.id, show_weather_example_string)
        bot.register_next_step_handler(city, get_weather)
    elif message.text == analyze_stock_button_string:
        stock = bot.send_message(message.chat.id, show_stock_message_string)
        bot.register_next_step_handler(stock, analyze_stock)
    elif message.text == finish_button_string:
        bot.send_message(message.chat.id, goodbye_string)
    else:
        begin(message.chat.id, dont_know_message_string)


@bot.message_handler(content_types=["text"])
def handle_docs_audio(message):
    bot.send_message(message.chat.id, text=error_string)


bot.infinity_polling()

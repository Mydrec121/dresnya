import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot("1854969870:AAEtLeBVWBQuZaQANzCA9n1PE2jiqgR_Yu4")


@bot.message_handler(commands=['start'])
def begin(message, text="Здравствуй. Что будем делать?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=3)
    k1 = types.KeyboardButton('Добавить товар в список')
    k2 = types.KeyboardButton('Показать список')
    k3 = types.KeyboardButton('Посчитать общую стоимость')
    k4 = types.KeyboardButton('Убрать одну покупку')
    k5 = types.KeyboardButton('Очистить список')
    k6 = types.KeyboardButton('Достаточно')
    k7 = types.KeyboardButton('свободная кнопка')
    k8 = types.KeyboardButton('свободная кнопка')
    keyboard.add(k1, k2, k3)
    keyboard.add(k4, k5, k6)
    keyboard.add(k7, k8)
    msg = bot.send_message(message.from_user.id, text=text, reply_markup=keyboard)

    bot.register_next_step_handler(msg, answer)
    a = sqlite3.connect('list.db')
    cursor = a.cursor()

    try:
        check = "CREATE TABLE \"list\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"item\" TEXT, PRIMARY KEY (\"ID\"))"
        cursor.execute(check)
    except:
        pass


def aditem(a):
    with sqlite3.connect('list.db') as i:
        cursor = i.cursor()
        cursor.execute('INSERT INTO list (user_id, item) VALUES (?, ?)', (a.from_user.id, a.text))
        i.commit()
    begin(a, "Добавил. Что ещё сделаем?")


def showlist(msg):
    with sqlite3.connect('list.db') as i:
        cursor = i.cursor()
        cursor.execute('SELECT item FROM list WHERE user_id=={}'.format(msg.from_user.id))
        a = cursor.fetchall()
        alist = []
        b = 1
        for q in list(enumerate(a)):
            alist.append(str(b) + '. ' + q[1][0] + '\n')
            b += 1
        a = ''.join(alist)
        bot.send_message(msg.chat.id, a)
        begin(msg, "Чем еще могу помочь?")


def count(msg):
    with sqlite3.connect('list.db') as i:
        cursor = i.cursor()
        cursor.execute('SELECT item FROM list WHERE user_id=={}'.format(msg.from_user.id))
        a = cursor.fetchall()
        b = 0
        for q in a:
            q = q[-1]
            q = q.split()
            b += float(q[1])
        bot.send_message(msg.chat.id, 'Итого набрано товаров на сумму: ' + str(b))
        begin(msg, "Чем еще могу помочь?")


def delitem(msg):
    delist = types.ReplyKeyboardMarkup(row_width=3)
    with sqlite3.connect('list.db') as i:
        cursor = i.cursor()
        cursor.execute('SELECT item FROM list WHERE user_id=={}'.format(msg.from_user.id))
        a = cursor.fetchall()
        for q in a:
            delist.add(types.KeyboardButton(q[0]))
        msg = bot.send_message(msg.from_user.id, text="Какой товар убрать?", reply_markup=delist)
        cursor.execute('DELETE FROM list WHERE user_id==? AND item==?', (msg.from_user.id, msg.text))
        begin(msg, "Удалил. Что-то ещё сделаем?")


def clist(msg):
    with sqlite3.connect('planner_hse.db') as i:
        cursor = i.cursor()
        cursor.execute('DELETE FROM list WHERE user_id=={}'.format(msg.from_user.id))
        i.commit()
    begin(msg, "Всё потёр. Что-то ещё сделаем?")


def answer(a):
    if a.text == "Добавить товар в список":
        msg = bot.send_message(a.chat.id,
                               'Запиши, что хочешь добавить, в формате "название цена (без знакак валюты)". Пример: "Хлеб 20"')
        bot.register_next_step_handler(msg, aditem)
    if a.text == "Показать список":
        try:
            showlist(a)
        except:
            bot.send_message(a.chat.id, 'Список пуст')
            begin(a, "Что-нибудь ещё?")
    if a.text == "Посчитать общую стоимость":
        try:
            count(a)
        except:
            bot.send_message(a.chat.id, 'Список пуст')
            begin(a, "Что-нибудь ещё?")
    if a.text == "Убрать одну покупку":
        try:
            delitem(a)
        except:
            bot.send_message(a.chat.id, 'Список уже пуст')
            begin(a, "Что-нибудь ещё?")
    if a.text == "Очистить список":
        try:
            clist(a)
        except:
            bot.send_message(a.chat.id, 'Список уже пуст')
            begin(a, "Что-нибудь ещё?")
    if a.text == "свободная кнопка":
        bot.send_message(a.chat.id, 'Коллеги, тут сделайте свою функцию')
        begin(a, "Что-нибудь ещё?")
    if a.text == "Достаточно":
        bot.send_message(a.chat.id, 'Тогда прощаюсь до следующей команды /start')


@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    begin(message, text="Моё сознание не охватывает данные сферы бытия. Попробуй спользовать кнопки")


bot.infinity_polling()

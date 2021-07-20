from datetime import datetime

from CRM_Tables import Customers, CustomersFromTg
from telebot import TeleBot
from sets import db
from envparse import Env

env = Env()
TOKEN = env.str("TOKEN")
bot = TeleBot(TOKEN)

access = False
username = "Empty"


@bot.message_handler(commands=['start', 'reg'])
def start(message):
    msg = bot.send_message(message.chat.id, "Привет, ти хочеш зареєструватись ?(y/n)")
    bot.register_next_step_handler(msg, choise)


@bot.message_handler(commands=['log_in'])
def log_in(message):
    msg = bot.send_message(message.chat.id, "Введи никнейм і пароль")
    bot.register_next_step_handler(msg, continue_log_in)


@bot.message_handler(commands=["subscribe_me"])
def subscribe_profile(message):
    global username, access
    if access:
        data_by_user_name = CustomersFromTg.query.filter(CustomersFromTg.username == username).first()
        data_by_user_name.is_subscribed = True
        db.session.commit()
        bot.send_message(message.chat.id, "Ти успішно підписався на повідомлення")
    else:
        bot.send_message(message.chat.id, "Для початку ввійди в аккунт /log_in")


@bot.message_handler(commands=["get"])
def subscribe_profile(message):
    global username, access
    bot.send_message(message.chat.id, username)




@bot.message_handler(commands=["unsubscribe_me"])
def unsubscribe_profile(message):
    global username, access
    if access:
        data_by_user_name = CustomersFromTg.query.filter(CustomersFromTg.username == username).first()
        data_by_user_name.is_subscribed = False
        db.session.commit()
        bot.send_message(message.chat.id, "Ти успішно відписався від повідомлент")
    else:
        bot.send_message(message.chat.id, "Для початку ввійди в аккунт /log_in")


def continue_log_in(message):
    data = message.text.split()
    if len(data) != 2:
        bot.send_message(message.chat.id, "Портібно ввести 2 слова /log_in")
    else:
        nickname, password = data
        data_by_nickname = Customers.query.filter(Customers.nickname == nickname).first()

        if data_by_nickname is None:
            bot.send_message(message.chat.id, 'Неправильний логін, спробуй ще раз /log_in')
        else:
            if data_by_nickname.password == password:
                bot.send_message(message.chat.id, 'Ти успішно ввійшов в свій акаунт, тепер тобі доступні деякі команди')
                global access, username
                access = True
                username = message.chat.username

                if data_by_nickname.telegram is None:
                    data_by_nickname.telegram = message.chat.username
                    db.session.commit()
                    CFT = CustomersFromTg(username=data_by_nickname.telegram,
                                          first_name=message.chat.first_name,
                                          last_name=message.chat.last_name,
                                          chat_id=message.chat.id,
                                          create_dt=datetime.utcnow())
                    db.session.add(CFT)
                    db.session.commit()
            else:
                bot.send_message(message.chat.id, 'Неправильний пароль, спробуй ще раз /log_in')


def choise(message):
    msg = message.text
    if msg == 'y':
        reg_new_user(message)
    elif msg == 'n':
        bot.send_message(message.chat.id, "Введи команду /log_in")
    else:
        bot.send_message(message.chat.id, "Введи тільки y або n /start")


def reg_new_user(message):
    msg = bot.send_message(message.chat.id, "Введи никнейм і пароль")
    bot.register_next_step_handler(msg, continue_reg_new_user)


def continue_reg_new_user(message):
    data = message.text.split()
    if len(data) != 2:
        bot.send_message(message.chat.id, "Портібно ввести 2 слова /start")
    else:
        nickname, password = data
        users_list = [i.nickname for i in Customers.query.all()]

        if nickname in users_list:
            bot.send_message(message.chat.id, 'Користува з таким никнеймом вже є в базі /start')
        else:
            user = Customers(nickname=nickname, password=password, create_dt=datetime.utcnow())
            db.session.add(user)
            db.session.commit()
            bot.send_message(message.chat.id, "Ти успішно зареєстрований /log_in")



bot.polling()
from datetime import datetime
from CRM_Tables import Customers, CustomersFromTg
from telebot import TeleBot
from sets import db
from envparse import Env

env = Env()
TOKEN = env.str("TOKEN")
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, вибери дію яку хоче зробити для початку /reg or /log_in")


@bot.message_handler(commands=['log_in'])
def log_in(message):
    msg = bot.send_message(message.chat.id, "Введи 𝐧𝐢𝐜𝐤𝐧𝐚𝐦𝐞 і 𝐩𝐚𝐬𝐬𝐰𝐨𝐫𝐝 ")
    bot.register_next_step_handler(msg, log_in_customer)


@bot.message_handler(commands=["subscribe_me"])
def subscribe_profile(message):
    global username, access
    if access:
        data_by_user_name = CustomersFromTg.query.filter(CustomersFromTg.username == username).first()
        if data_by_user_name.is_subscribed:
            bot.send_message(message.chat.id, "Ти вже підисаний на повідомлення")
        else:
            data_by_user_name.is_subscribed = True
            db.session.commit()
            bot.send_message(message.chat.id, "Ти успішно підписався на повідомлення")
    else:
        bot.send_message(message.chat.id, "Для початку ввійди в аккунт /log_in")


@bot.message_handler(commands=["unsubscribe_me"])
def unsubscribe_profile(message):
    global username, access
    if access:
        data_by_user_name = CustomersFromTg.query.filter(CustomersFromTg.username == username).first()
        if not data_by_user_name.is_subscribed:
            bot.send_message(message.chat.id, "Ти вже відписаний від повідомлення")
        else:
            data_by_user_name.is_subscribed = False
            db.session.commit()
            bot.send_message(message.chat.id, "Ти успішно відписався від повідомлень")
    else:
        bot.send_message(message.chat.id, "Для початку ввійди в аккунт /log_in")


def log_in_customer(message):
    data = message.text.split()
    if len(data) != 2:
        bot.send_message(message.chat.id, "Портібно ввести 2 слова /log_in")
    else:
        nickname, password = data
        get_user_id = Customers.query.filter(Customers.nickname == nickname).first()

        if get_user_id is None:
            bot.send_message(message.chat.id, 'Неправильний логін, спробуй ще раз /log_in')
        else:
            if get_user_id.password == password:
                bot.send_message(message.chat.id, 'Ти успішно ввійшов в свій акаунт, тепер тобі доступні деякі команди')
                global access, username
                username = message.chat.username
                access = True
            else:
                bot.send_message(message.chat.id, 'Неправильний пароль, спробуй ще раз /log_in')


@bot.message_handler(commands=['reg'])
def reg(message):
    username_list = [i.username for i in CustomersFromTg.query.all()]

    if message.chat.username in username_list:
        msg = bot.send_message(message.chat.id, "Ваш username уже зареєстрований, хочете створити новий акаунт? (y/n)")
        bot.register_next_step_handler(msg, choise)
    else:
        msg = bot.send_message(message.chat.id, "Для регестарції введи новий 𝐧𝐢𝐜𝐤𝐧𝐚𝐦𝐞 і 𝐩𝐚𝐬𝐬𝐰𝐨𝐫𝐝 ")
        bot.register_next_step_handler(msg, reg_customer)


def reg_customer(message):
    data = message.text.split()
    if len(data) != 2:
        bot.send_message(message.chat.id, "Портібно ввести 2 слова /reg")
    else:
        nickname, password = data
        users_list = [i.nickname for i in Customers.query.all()]

        if nickname in users_list:
            bot.send_message(message.chat.id, 'Користува з таким никнеймом вже є в базі /start')
        else:
            user = Customers(nickname=nickname,
                             password=password,
                             create_dt=datetime.utcnow())
            db.session.add(user)
            db.session.commit()
            bot.send_message(message.chat.id, f"Ти успішно зареєстрований /log_in, твій id: {user.user_id}")

            save_in_table(message, nickname)


def choise(message):
    msg = message.text
    if msg == 'y':
        TgCustomers_data = CustomersFromTg.query.filter(CustomersFromTg.username == message.chat.username).first()
        Customers_data = Customers.query.filter(Customers.user_id == TgCustomers_data.customer_id).first()
        db.session.delete(TgCustomers_data)
        db.session.commit()
        db.session.delete(Customers_data)
        db.session.commit()

        msg = bot.send_message(message.chat.id, "Для регестарції введи новий 𝐧𝐢𝐜𝐤𝐧𝐚𝐦𝐞 і 𝐩𝐚𝐬𝐬𝐰𝐨𝐫𝐝 ")
        bot.register_next_step_handler(msg, reg_customer)
    else:
        bot.send_message(message.chat.id, "Введи логін щоб увійти в акаунт /log_in")


def save_in_table(message, nickname):
    get_user = Customers.query.filter(Customers.nickname == nickname).first()
    CFT = CustomersFromTg(username=message.chat.username,
                          first_name=message.chat.first_name,
                          last_name=message.chat.last_name,
                          chat_id=message.chat.id,
                          customer_id=get_user.user_id,
                          create_dt=datetime.utcnow())
    db.session.add(CFT)
    db.session.commit()


bot.polling()
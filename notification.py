import requests
from envparse import Env
from models import Orders, Employees

API = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s'

env = Env()
TOKEN = env.str("TOKEN")


def order_notifications(chat_it, action, id_):
    message = f"Your order has been {action}, with: {id_} Id "
    requests.get(API % (TOKEN, chat_it, message))


def employee_notification(chat_id, order_id):
    text = f'Your new order.\n' \
           f'Id: {order_id}\n'
    requests.get(API % (TOKEN, chat_id, text))


def daily_notify():
    text = 'Your orders for today.\n'
    order_data = Orders.query.all()
    employee_data = Employees.query.all()
    for employee in employee_data:
        requests.get(API % (TOKEN, employee.chat_id, text))
        for order in order_data:
            if employee.employee_id == order.creator_id and order.ord_status == 'Active':
                requests.get(API % (TOKEN, employee.chat_id, order))

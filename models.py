from datetime import datetime
from sets import db


class CustomersFromTg(db.Model):
    __tablename__ = 'CustomersFromTg'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.user_id'), unique=True, nullable=False)
    access = db.Column(db.String)

    is_subscribed = db.Column(db.Boolean, default=False)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())


class Customers(db.Model):
    __tablename__ = 'Customers'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    nickname = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())


class Departments(db.Model):
    __tablename__ = 'Deparments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(50), unique=True)
    create_dt = db.Column(db.DateTime, default=datetime.now().date())
    update_dt = db.Column(db.DateTime)

    def __str__(self):
        return f"Id: {self.id}, Name: {self.department_name}, Create: {self.create_dt}, Update: {self.update_dt}"


class Employees(db.Model):
    __tablename__ = 'Employees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('Deparments.id'), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    tg_username = db.Column(db.Integer, nullable=False)
    create_dt = db.Column(db.DateTime, default=datetime.now().date())
    update_dt = db.Column(db.DateTime)

    def __str__(self):
        return f"Id: {self.id}, " \
               f"Fio: {self.fio}, " \
               f"Position: {self.position}, " \
               f"Department Id: {self.department_id}, " \
               f"Telegram username: {self.tg_username}, " \
               f"Chat id: {self.chat_id}, " \
               f"Create: {self.create_dt}, " \
               f"Update: {self.update_dt}"


class Orders(db.Model):
    __tablename__ = 'Orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_type = db.Column(db.String(100), nullable=False)
    descriptions = db.Column(db.String(500))
    status = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('Employees.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.user_id'), nullable=False)
    create_dt = db.Column(db.DateTime, default=datetime.now().date())
    update_dt = db.Column(db.DateTime)

    def __str__(self):
        return f"Id: {self.id}, " \
               f"Order Type: {self.order_type}, " \
               f"Descriptions: {self.descriptions}, " \
               f"Status: {self.status}, "  \
               f"Creator Id: {self.create_dt}, " \
               f"Customer Id: {self.customer_id}, " \
               f"Create: {self.create_dt}, " \
               f"Update: {self.update_dt}"


if __name__ == "__main__":
    db.create_all()

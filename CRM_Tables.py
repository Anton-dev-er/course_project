from datetime import datetime
from sets import db


class CustomersFromTg(db.Model):
    __tablename__ = 'CustomersFromTg'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String, db.ForeignKey('Customers.telegram'), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)

    is_subscribed = db.Column(db.Boolean, default=False)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())


class Customers(db.Model):
    __tablename__ = 'Customers'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    nickname = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    telegram = db.Column(db.String(100), unique=True)

    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())


class Departments(db.Model):
    __tablename__ = 'Deparments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(50), unique=True)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())


class Employees(db.Model):
    __tablename__ = 'Employees'

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())
    department_id = db.Column(db.Integer, db.ForeignKey('Deparments.department_id'), nullable=False)


class Orders(db.Model):
    __tablename__ = 'Orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_type = db.Column(db.String(100), nullable=False)
    descriptions = db.Column(db.String(500))
    status = db.Column(db.String(100), nullable=False)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow().date())
    creator_id = db.Column(db.Integer, db.ForeignKey('Employees.employee_id'), nullable=False)
    customer = db.Column(db.Integer, db.ForeignKey('Customers.user_id'), nullable=False, unique=True)


if __name__ == "__main__":
    db.create_all()

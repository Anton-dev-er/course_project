import json
from datetime import datetime
from json import JSONDecodeError
import sqlalchemy.exc
from flask import request, render_template
from models import Departments, Employees, Orders, Customers, CustomersFromTg
from sets import db, my_app
from notification import order_notifications, employee_notification


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return True
    return False


def get_columns_by_class(cls):
    dct = {Departments: ["department_name"],
           Employees: ["fio", "position", "department_id", "tg_username", "chat_id"],
           Orders: ["order_type", "descriptions", "status", "tg_mickname", "creator_id"]}
    return dct[cls]


def insert_into_db(data, cls):
    if issubclass(cls, Orders):
        get_creator_id = Employees.query.get(data["creator_id"])
        get_customer = Customers.query.filter_by(nickname=str(data["tg_mickname"])).first()
        get_tg_customer = CustomersFromTg.query.filter_by(user_id=get_customer.user_id).first()
        if (get_customer is not None) and (get_creator_id is not None) and (get_tg_customer is not None):
            if data["status"] == "Active" or data["status"] == "Closed":
                o = Orders(order_type=data["order_type"],
                           descriptions=data["descriptions"],
                           status=data["status"],
                           customer_id=get_customer.user_id,
                           creator_id=get_creator_id.id)
                order_notifications(get_tg_customer.chat_id, o.id, "created")
            else:
                raise KeyError("order_type shuold be Acitve or Closed")
        else:
            raise KeyError("Wrond creator_id or customer_id")
    elif issubclass(cls, Employees):
        get_deparment_id = Departments.query.get(data["department_id"])
        if get_deparment_id is not None:
            e = Employees(fio=data["fio"],
                          position=data["position"],
                          department_id=get_deparment_id.id,
                          tg_username=data["tg_username"],
                          chat_id=data["chat_id"])
            employee_notification(e.chat_id, e.id)
            return e
        else:
            raise KeyError("Wrong department_id")
    elif issubclass(cls, Departments):
        return Departments(department_name=data["department_name"])


def get_lists_id(cls):
    return [i.id for i in cls.query.all()]


def create_validator(cls):
    try:
        param_list = get_columns_by_class(cls)

        if request.data == b'':
            raise ValueError

        data = json.loads(request.data)

        if sorted(data.keys()) != sorted(param_list) or is_json(request.data):
            raise ValueError

        insert_query = insert_into_db(data, cls)

        db.session.add(insert_query)
        db.session.commit()

    except sqlalchemy.exc.IntegrityError:
        return "Already exist"
    except ValueError:
        return f"Should be a format dict or json (with keys: {param_list})"
    except KeyError as e:
        return f"{e}"

    return f"Successfully created, ID: {insert_query.id}"


def delete_validator(id_, cls):
    try:
        db.session.delete(cls.query.get(id_))
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        return exc
    return "Successfully deleted"


def update_value(class_instance, column, new_value):
    if column in ["department_name"]:
        class_instance.department_name = new_value
        return True
    elif column in ["fio", "position", "tg_username", "chat_id"]:
        if column == "fio":
            class_instance.fio = new_value
        elif column == "tg_username":
            class_instance.tg_username = new_value
        elif column == "chat_id":
            class_instance.chat_id = new_value
        elif column == "position":
            class_instance.position = new_value
        return True
    elif column in ["order_type", "descriptions", "status", "customer_id"]:
        if column == "order_type":
            class_instance.order_type = new_value
        elif column == "descriptions":
            class_instance.descriptions = new_value
        elif column == "status":
            class_instance.status = new_value
        return True
    return False


def update_validator(column, cls):
    try:
        data = json.loads(request.data)
    except JSONDecodeError:
        return f"Body should be json"

    if sorted(data.keys()) != sorted(["Id", "New_value"]):
        return f'Should be a format dict or json (with keys: {["Id", "New_value"]})'

    if check_id(data["Id"], cls):
        return "Non-existent id"

    class_instance = cls.query.get(data["Id"])

    if update_value(class_instance, column, data["New_value"]):
        class_instance.update_dt = datetime.now().date()

        db.session.add(class_instance)
        db.session.commit()
        chat_id = get_chat_id_for_order(data["Id"])
        order_notifications(chat_id, data["Id"], "update")
        return "Successfully updated"
    else:
        column_list = {Departments: ["department_name"],
                       Employees: ["fio", "position", "tg_username", "chat_id"],
                       Orders: ["order_type", "descriptions", "status"]}[cls]
        return f"Wrong column, allowed columns {column_list}"


def check_id(id_, cls):
    list_id = get_lists_id(cls)

    if id_ not in list_id:
        return True

    return False


@my_app.route("/", methods=["GET"])
def mainpage():
    return render_template("mainpage.html")


# Create routes
@my_app.route("/departments/create", methods=["POST"])
def dep_create_new_param():
    return create_validator(Departments)


@my_app.route("/employees/create", methods=["POST"])
def emp_create_new_param():
    return create_validator(Employees)


@my_app.route("/orders/create", methods=["POST"])
def ord_create_new_param():
    return create_validator(Orders)


# Get routes
@my_app.route("/departments/get/all", methods=["GET"])
def dep_get_data():
    return render_template('show_department.html', data=[i for i in Departments.query.all()])


@my_app.route("/employees/get/all", methods=["GET"])
def emp_get_data():
    return render_template('show_employee.html', data=[i for i in Employees.query.all()])


@my_app.route("/orders/get/all", methods=["GET"])
def ord_get_data():
    return render_template('show_order.html', data=[i for i in Orders.query.all()])


@my_app.route("/departments/get/<int:id_>", methods=["GET"])
def dep_get_data_by_id(id_):
    if check_id(id_, Departments):
        return "Non-existent id"
    return render_template('show_order.html', data=[Departments.query.get(id_)])


@my_app.route("/employees/get/<int:id_>", methods=["GET"])
def emp_get_data_by_id(id_):
    if check_id(id_, Employees):
        return "Non-existent id"
    return render_template('show_order.html', data=[Employees.query.get(id_)])


@my_app.route("/orders/get/<int:id_>", methods=["GET"])
def ord_get_data_by_id(id_):
    if check_id(id_, Orders):
        return "Non-existent id"
    return render_template('show_order.html', data=[Orders.query.get(id_)])


# Delete routes
@my_app.route("/departments/delete/<int:id_>", methods=["DELETE"])
def dep_delete_data_by_id(id_):
    if check_id(id_, Departments):
        return "Non-existent id"
    return delete_validator(id_=id_, cls=Departments)


@my_app.route("/employees/delete/<int:id_>", methods=["DELETE"])
def emp_delete_data_by_id(id_):
    if check_id(id_, Employees):
        return "Non-existent id"
    return delete_validator(id_=id_, cls=Employees)


@my_app.route("/orders/delete/<int:id_>", methods=["DELETE"])
def ord_delete_data_by_id(id_):
    if not check_id(id_, Orders):
        chat_id = get_chat_id_for_order(id_)
        order_notifications(chat_id, id_, "deleted")
        return delete_validator(id_=id_, cls=Orders)
    else:
        return "non-existent id"


def get_chat_id_for_order(id_):
    if not check_id(id_, Orders):
        order = Orders.query.get(id_)
        get_customer = Customers.query.filter_by(user_id=order.customer_id).first()
        get_tg_customer = CustomersFromTg.query.filter_by(user_id=get_customer.user_id).first()
        return get_tg_customer.chat_id


# Update toutes
@my_app.route("/departments/update/<string:column>", methods=["POST"])
def dep_update_data_by_id(column):
    return update_validator(column, Departments)


@my_app.route("/employees/update/<string:column>", methods=["POST"])
def emp_update_data_by_id(column):
    return update_validator(column, Employees)


@my_app.route("/orders/update/<string:column>", methods=["POST"])
def ord_update_data_by_id(column):
    return update_validator(column, Orders)


# Filters
@my_app.route("/fiters/get/orders/by_customer_id/<int:id_>",  methods=["GET"])
def get_orders_by_cutomers(id_):
    data = Orders.query.filter_by(customer_id=id_).all()
    return render_template("show_filters.html", data=[i for i in data], title="Orders by cutomer id")


@my_app.route("/fiters/get/orders/by_date",  methods=["GET"])
def get_orders_by_date():
    try:
        data = json.loads(request.data)
    except JSONDecodeError:
        return f"Body should be json"

    if "start_date" in data and "end_date" in data:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        dates = Orders.query.filter(Orders.create_dt >= start_date, Orders.create_dt <= end_date).all()
        return render_template('show_order.html', data=[i for i in dates])
    elif "start_date" in data:
        dates = Orders.query.filter(Orders.create_dt >= data['start_date']).all()
        return render_template("show_filters.html", data=[i for i in dates], title="Orders by dates")
    else:
        return f'Should be a format dict or json (with keys: {"start_date", "end_date"} or {"start_date"})'


@my_app.route("/fiters/get/orders/by_status",  methods=["GET"])
def get_orders_by_status():
    try:
        data = json.loads(request.data)
    except JSONDecodeError:
        return f"Body should be json"

    if "status" not in data.keys():
        return "Should be a format dict or json (with keys: 'status')"

    statuses = Orders.query.filter_by(status=data['status']).all()
    return render_template("show_filters.html", data=[i for i in statuses], title="Orders by status")


@my_app.route("/fiters/get/orders/by_creator_id/<int:id_>", methods=['GET'])
def get_orders_by_creator_id(id_):
    data = Orders.query.filter_by(creator_id=id_).all()
    return render_template("show_filters.html", data=[i for i in data], title="Orders by creator id")


if __name__ == "__main__":
    my_app.run()

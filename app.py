import json
from datetime import datetime
from json import JSONDecodeError
import sqlalchemy.exc
from flask import request, render_template
from CRM_Tables import Departments, Employees, Orders, Customers
from sets import db, my_app


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return True
    return False


def department_get_dict(d):
    return {"Name": d.department_name,
            "Id": d.id,
            "Create date": str(d.create_dt),
            "Update date": str(d.update_dt)}


def employ_get_dict(e):
    return {"ID": e.id,
            "Fio": e.fio,
            "Position": e.position,
            "Department ID": e.department_id,
            "Create date": str(e.create_dt),
            "Update date": str(e.update_dt)}


def order_get_dict(o):
    return {"ID": o.id,
            "Order type": o.order_type,
            "Descriptions": o.descriptions,
            "Status": o.status,
            "Creator ID": o.creator_id,
            "Customer Id": o.customer_id,
            "Create date": str(o.create_dt),
            "Update date": str(o.update_dt)}


def customer_get_dict(c):
    return {"ID": c.user_id,
            "Nickname": c.nickname,
            "Password": c.password,
            "Create date": c.create_dt
            }


def get_columns_by_class(cls):
    dct = {Departments: ["department_name"],
           Employees: ["fio", "position", "department_id"],
           Orders: ["order_type", "descriptions", "status", "customer_id", "creator_id"]}
    return dct[cls]


def get_insert_querys_by_class(data, cls):
    if issubclass(cls, Orders):
        get_creator_id = Employees.query.get(data["creator_id"])
        get_nickname = Customers.query.get(data["customer_id"])
        if get_nickname is not None and get_creator_id is not None:
            if data["status"] == "Active" or data["status"] == "Closed":
                return Orders(order_type=data["order_type"],
                              descriptions=data["descriptions"],
                              status=data["status"],
                              customer_id=get_nickname.user_id,
                              creator_id=get_creator_id.id)
            else:
                raise KeyError("order_type shuold be Acitve or Closed")
        else:
            raise KeyError("Wrond creator_id or customer_id")
    elif issubclass(cls, Employees):
        get_deparment_id = Departments.query.get(data["department_id"])
        if get_deparment_id is not None:
            return Employees(fio=data["fio"],
                             position=data["position"],
                             department_id=get_deparment_id.id)
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

        insert_query = get_insert_querys_by_class(data, cls)

        db.session.add(insert_query)
        db.session.commit()

    except sqlalchemy.exc.IntegrityError:
        return "Already exist"
    except ValueError:
        return f"Should be a format dict or json (with keys: {param_list})"
    except KeyError as e:
        return f"{e}"

    return f"Successfully created, ID: {insert_query.id}"


def delete_validator(id_, list_id, cls):
    try:
        if id_ not in list_id:
            return "Wrong param"
        db.session.delete(cls.query.get(id_))
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        return exc
    return "Successfully deleted"


def update_value(class_instance, column, new_value):
    if column in ["department_name"]:
        class_instance.department_name = new_value
        return True
    elif column in ["fio", "position"]:
        if column == "fio":
            class_instance.fio = new_value
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
        return "Successfully updated"
    else:
        column_list = {Departments: ["department_name"],
                       Employees: ["fio", "position"],
                       Orders: ["order_type", "descriptions", "status"]}[cls]
        return f"Wrong column, allowed columns {column_list}"


def check_id(id_, cls):
    list_id = get_lists_id(cls)

    if id_ not in list_id:
        return True

    return False


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
    return render_template('get_data.html', lst=[department_get_dict(i) for i in Departments.query.all()])


@my_app.route("/employees/get/all", methods=["GET"])
def emp_get_data():
    return render_template('get_data.html', lst=[employ_get_dict(i) for i in Employees.query.all()])


@my_app.route("/orders/get/all", methods=["GET"])
def ord_get_data():
    return render_template('get_data.html', lst=[order_get_dict(i) for i in Orders.query.all()])


@my_app.route("/customers/get/all", methods=["GET"])
def cust_get_data():
    return render_template('get_data.html', lst=[customer_get_dict(i) for i in Customers.query.all()])


@my_app.route("/departments/get/<int:id_>", methods=["GET"])
def dep_get_data_by_id(id_):
    if check_id(id_, Departments):
        return "Non-existent id"
    return department_get_dict(Departments.query.get(id_))


@my_app.route("/employees/get/<int:id_>", methods=["GET"])
def emp_get_data_by_id(id_):
    if check_id(id_, Employees):
        return "Non-existent id"
    return employ_get_dict(Employees.query.get(id_))


@my_app.route("/orders/get/<int:id_>", methods=["GET"])
def ord_get_data_by_id(id_):
    if check_id(id_, Orders):
        return "Non-existent id"
    return order_get_dict(Orders.query.get(id_))


# Delete routes
@my_app.route("/departments/delete/<int:id_>", methods=["DELETE"])
def dep_delete_data_by_id(id_):
    list_id = get_lists_id(Departments)
    return delete_validator(id_=id_, list_id=list_id, cls=Departments)


@my_app.route("/employees/delete/<int:id_>", methods=["DELETE"])
def emp_delete_data_by_id(id_):
    list_id = get_lists_id(Employees)
    return delete_validator(id_=id_, list_id=list_id, cls=Employees)


@my_app.route("/orders/delete/<int:id_>", methods=["DELETE"])
def ord_delete_data_by_id(id_):
    list_id = get_lists_id(Orders)
    return delete_validator(id_=id_, list_id=list_id, cls=Orders)


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
    return render_template('get_data.html', lst=[order_get_dict(i) for i in data])


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
        return render_template('get_data.html', lst=[order_get_dict(i) for i in dates])
    elif "start_date" in data:
        dates = Orders.query.filter(Orders.create_dt >= data['start_date']).all()
        return render_template('get_data.html', lst=[order_get_dict(i) for i in dates])
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
    return render_template('get_data.html', lst=[order_get_dict(i) for i in statuses])


@my_app.route("/fiters/get/orders/by_creator_id/<int:id_>", methods=['GET'])
def get_orders_by_creator_id(id_):
    data = Orders.query.filter_by(creator_id=id_).all()
    return render_template('get_data.html', lst=[order_get_dict(i) for i in data])


if __name__ == "__main__":
    my_app.run()

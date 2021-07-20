import json

import sqlalchemy.exc
from envparse import Env
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from CRM_Tables import Departments, Employees, Orders


env = Env()
DB_URL = env.str("DB_URL")


my_app = Flask(__name__)
my_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
my_app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(my_app)


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return True
    return False


def dep_get_dict(d):
    return {"Name": d.department_name,
            "Id": d.department_id,
            "Create date": str(d.create_dt)}


def emp_get_dict(e):
    return {"ID": e.employee_id,
            "Fio": e.fio,
            "Position": e.position,
            "Create date": str(e.create_dt),
            "Department ID": e.department_id
            }


def ord_get_dict(o):
    return {"ID": o.order_id,
            "Order type": o.order_type,
            "Descriptions": o.descriptions,
            "Status": o.status,
            "Create date": str(o.create_dt),
            "Creator ID": o.creator_id,
            "Customer": o.customer
            }


def get_columns_by_class(cls):
    dct = {Departments: ["department_name"],
           Employees: ["fio", "position", "department_id"],
           Orders: ["order_type", "descriptions", "status", "customer", "creator_id"]}
    return dct[cls]


def get_insert_querys_by_class(data, cls):
    deparment = Departments.query.get(data["department_id"])
    employee = Employees.query.get(data["creator_id"])

    dct = {Departments: Departments(department_name=data["department_name"]),
           Employees: Employees(fio=data["fio"],
                                position=data["position"],
                                department_id=deparment.department_id),
           Orders: Orders(order_type=data["order_type"],
                          descriptions=data["descriptions"],
                          status=data["status"],
                          customer=data["customer"],
                          creator_id=employee.creator_id)
           }
    return dct[cls]


def get_column_dict_for_update(class_instance, cls):
    dct = {
        Departments: {
            "department_name": class_instance.department_name},
        Employees: {
            "fio": class_instance.fio,
            "position": class_instance.position},
        Orders: {
            "order_type": class_instance.order_type,
            "descriptions": class_instance.descriptions,
            "status": class_instance.status,
            "serial_no": class_instance.serial_no}
            }
    return dct[cls]


def get_lists_id():
    return {Departments: [i.department_id for i in Departments.query.all()],
            Employees: [i.employee_id for i in Employees.query.all()],
            Orders: [i.order_id for i in Orders.query.all()]
            }


def for_create_new_param(cls):
    try:
        param_list = get_columns_by_class(cls)

        if request.data == b'':
            raise ValueError

        data = json.loads(request.data)

        if sorted(data.keys()) != sorted(param_list) and is_json(request.data):
            raise ValueError

        insert_query = get_insert_querys_by_class(data, cls)

        db.session.add(insert_query)
        db.session.commit()

    except sqlalchemy.exc.IntegrityError:
        return "Already exist"
    except ValueError:
        return f"Should be a format dict or json (with keys like:{param_list})"

    return "Successfully created"


def check_id(id_, cls):
    lists_id = get_lists_id()

    if cls not in lists_id:
        return True

    list_id = lists_id[cls]

    if id_ not in list_id:
        return True

    return False


@my_app.route("/departments/create", methods=["POST"])
def dep_create_new_param():
    return for_create_new_param(Departments)


@my_app.route("/employees/create", methods=["POST"])
def emp_create_new_param():
    return for_create_new_param(Employees)


@my_app.route("/orders/create", methods=["POST"])
def ord_create_new_param():
    return for_create_new_param(Orders)


@my_app.route("/departments/get/all", methods=["GET"])
def dep_get_data():
    return render_template('get_data.html', lst=[dep_get_dict(i) for i in Departments.query.all()])


@my_app.route("/employees/get/all", methods=["GET"])
def emp_get_data():
    return render_template('get_data.html', lst=[emp_get_dict(i) for i in Employees.query.all()])


@my_app.route("/orders/get/all", methods=["GET"])
def ord_get_data():
    return render_template('get_data.html', lst=[ord_get_dict(i) for i in Orders.query.all()])


@my_app.route("/departments/get/<int:id_>", methods=["GET"])
def dep_get_data_by_id(id_):
    if check_id(id_, Departments):
        return "Non-existent id or class"
    return dep_get_dict(Departments.query.get(id_))


@my_app.route("/employees/get/<int:id_>", methods=["GET"])
def emp_get_data_by_id(id_):
    if check_id(id_, Employees):
        return "Non-existent id or class"
    return emp_get_dict(Employees.query.get(id_))


@my_app.route("/orders/get/<int:id_>", methods=["GET"])
def ord_get_data_by_id(id_):
    if check_id(id_, Orders):
        return "Non-existent id or class"
    return dep_get_dict(Orders.query.get(id_))


def for_delete_data_by_id(id_, list_id, cls):
    try:
        if id_ not in list_id:
            return "Wrong param"
        db.session.delete(cls.query.get(id_))
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return "Key (department_id)=(1) is still referenced from table 'employees'"
    return "Successfully deleted"


@my_app.route("/departments/delete/<int:id_>", methods=["DELETE"])
def dep_delete_data_by_id(id_):
    list_id = get_lists_id()[Departments]
    return for_delete_data_by_id(id_=id_, list_id=list_id, cls=Departments)


@my_app.route("/employees/delete/<int:id_>", methods=["DELETE"])
def emp_delete_data_by_id(id_):
    list_id = get_lists_id()[Employees]
    return for_delete_data_by_id(id_=id_, list_id=list_id, cls=Employees)


@my_app.route("/orders/delete/<int:id_>", methods=["DELETE"])
def ord_delete_data_by_id(id_):
    list_id = get_lists_id()[Orders]
    return for_delete_data_by_id(id_=id_, list_id=list_id, cls=Orders)


@my_app.route("/departments/update/<string:column>", methods=["POST"])
def dep_update_data_by_id(column):
    data = json.loads(request.data)

    if sorted(data.keys()) != sorted(["Id", "New_value"]):
        return f'Should be a format dict or json (with keys like:{["Id", "New_value"]})'

    if check_id(data["Id"], Departments):
        return "Non-existent id or class"

    deparment = Departments.query.get(data["Id"])
    column_list = get_column_dict_for_update(deparment, Departments)

    if column in column_list.keys():
        column_list[column] = data["New_value"]
    else:
        return "Wrong column"
    return "Successfully updated"


@my_app.route("/employees/update/<string:column>", methods=["POST"])
def emp_update_data_by_id(column):
    data = json.loads(request.data)

    if sorted(data.keys()) != sorted(["Id", "New_value"]):
        return f'Should be a format dict or json (with keys like:{["Id", "New_value"]})'

    if check_id(data["Id"], Employees):
        return "Non-existent id or class"

    employe = Employees.query.get(data["Id"])
    column_list = get_column_dict_for_update(employe, Employees)

    if column in column_list.keys():
        column_list[column] = data["New_value"]
    else:
        return "Wrong column"
    return "Successfully updated"


@my_app.route("/orders/update/<string:column>", methods=["POST"])
def ord_update_data_by_id(column):
    data = json.loads(request.data)

    if sorted(data.keys()) != sorted(["Id", "New_value"]):
        return f'Should be a format dict or json (with keys like:{["Id", "New_value"]})'

    if check_id(data["Id"], Orders):
        return "Non-existent id or class"

    order = Orders.query.get(data["Id"])

    column_list = get_column_dict_for_update(order, Orders)

    if column in column_list.keys():
        column_list[column] = data["New_value"]
    else:
        return "Wrong column"
    return "Successfully updated"


if __name__ == "__main__":
    my_app.run()

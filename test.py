from CRM_Tables import *

param_lists = {
            Departments: ["department_name"],
            Employees: ["fio", "position", "department_id"],
            Orders: ["order_type", "descriptions", "status", "customer", "creator_id"]
        }

print(Departments in param_lists)


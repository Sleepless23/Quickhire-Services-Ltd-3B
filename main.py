import json

employee_file = "employees.json"
attendace_file = "attendance.json"

#employee class to initialize variables

class Employee:

    def __init__(self, emp_id, name, role, dept, rate, contact):
        self.emp_id = emp_id
        self.name = name
        self.role = role
        self.dept = dept
        self.rate = rate
        self.contact = contact
    
    #dictionary to save the employees info

    def my_dict(self):
        return{
            "emp_id": self.emp_id,
            "name": self.name,
            "role": self.role,
            "dept": self.dept,
            "rate": self.rate,
            "contact": self.contact
        }

#funtion to load data
def load_data(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except:
        return []
    
#function to save data
def save_data(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent = 4)

#funtion to register employees
def register_employees():
    employees = load_data(employee_file)
    emp_id = len(employees) + 1

    print("\n---Register New Employee---")
    name = input("Name: ")
    role = input("Role: ")
    dept = input("Department: ")
    rate = float(input("Hourly Rate: "))
    contact = input("Contact: ")

    emp = Employee(emp_id,name, role, dept, rate, contact)
    employees.append(emp.my_dict())

    save_data(employee_file, employees)
    print("Employee Registered Successfully")


register_employees()

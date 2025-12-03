import json
from datetime import datetime

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
    
    # To get the highest id then add 1 to prevent duplicating ids
    highest_id = 0
    for emp in employees:
        if emp["emp_id"] > highest_id:
            highest_id = emp["emp_id"]

    emp_id = highest_id + 1
    
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

def edit_employee():
    employees = load_data(employee_file)
    emp_id = int(input("Enter employee ID to edit: "))

    for emp in employees:
        if emp["emp_id"] == emp_id:
            print(f"Editing Employee: {emp["name"]}")
            emp["name"] = input("New Name: ")
            emp["role"] = input("New Role: ")
            emp["dept"] = input("New Department: ")
            emp["rate"] = float(input("New Hourly Rate: "))
            emp["contact"] = input("New Contact: ")

            save_data(employee_file, employees)
            print("Employee Successfully Updated")
            return
    print("Employee Not Found!")

def delete_employee():
    employees = load_data(employee_file)
    emp_id = int(input("Enter employee ID to delete employee: "))

    updated_employees = []

    for employee in employees:
        if employee["emp_id"] != emp_id:
            updated_employees.append(employee)
    
    save_data(employee_file, updated_employees)

    print("Employee Successfully Removed!")


    # SIGN IN!
def sign_in():
    attendance = load_data(attendace_file)
    emp_id = int(input("Enter Employee ID: "))
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if already signed in
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == today and not entry.get("sign_out"):
            print("Already signed in today!")
            return
    
    sign_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        "emp_id": emp_id,
        "date": today,
        "sign_in": sign_in_time,
        "sign_out": None,
        "hours": 0.0
    }
    attendance.append(new_entry)
    save_data(attendace_file, attendance)
    print("Signed in successfully!")

# SIGN OUT!
def sign_out():
    attendance = load_data(attendace_file)
    emp_id = int(input("Enter Employee ID: "))
    today = datetime.now().strftime("%Y-%m-%d")
    
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == today and not entry.get("sign_out"):
            sign_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry["sign_out"] = sign_out_time
            
            # Calculate hours
            in_time = datetime.strptime(entry["sign_in"], "%Y-%m-%d %H:%M:%S")
            out_time = datetime.strptime(sign_out_time, "%Y-%m-%d %H:%M:%S")
            hours = (out_time - in_time).total_seconds() / 3600
            entry["hours"] = round(hours, 2)
            
            save_data(attendace_file, attendance)
            print(f"Signed out! Hours today: {entry['hours']}")
            return
    
    print("No sign-in found for today!")

def menu():

    while True:
        print("""
===============================
    QuickHire-Services-Ltd.
===============================
              
1. Register Employee
2. Edit Employee
3. Delete Employee
4. Sign In
5. Sign Out
""")

        choice = int(input("Select Option: "))

        if choice == 1:
            register_employees()
        elif choice == 2:
            edit_employee()
        elif choice == 3:
            delete_employee()
        elif choice == 4:
            sign_in()
        elif choice == 5:
            sign_out()
        
menu()



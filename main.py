import json
from datetime import datetime

employee_file = "employees.json"
attendance_file = "attendance.json"
hr_pass = "admin_123"

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
    attendance = load_data(attendance_file)
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    today = datetime.now().strftime("%m-%d-%Y")
    # Check if already signed in
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == today and not entry.get("sign_out"):
            print("Already signed in today!")
            return
    
    sign_in_time = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    new_entry = {
        "emp_id": emp_id,
        "date": today,
        "sign_in": sign_in_time,
        "sign_out": None,
        "hours": 0.0
    }
    attendance.append(new_entry)
    save_data(attendance_file, attendance)
    print("Signed in successfully!")

# SIGN OUT!
def sign_out():
    attendance = load_data(attendance_file)
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    today = datetime.now().strftime("%m-%d-%Y")
    
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == today and not entry.get("sign_out"):
            sign_out_time = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
            entry["sign_out"] = sign_out_time
            
            # Calculate hours
            in_time = datetime.strptime(entry["sign_in"], "%m-%d-%Y %H:%M:%S")
            out_time = datetime.strptime(sign_out_time, "%m-%d-%Y %H:%M:%S")
            hours = (out_time - in_time).total_seconds() / 3600
            entry["hours"] = round(hours, 2)
            
            save_data(attendance_file, attendance)
            print(f"Signed out! Hours today: {entry['hours']}")
            return
    
    print("No sign-in found for today!")

# HR Attendance Correction
def edit_attendance():
    password = input("Enter HR Password: ")
    if password != hr_pass:
        print("Access denied! For HR only!")
        return
    
    attendance = load_data(attendance_file)
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID Number.")
        return
    
    date = input("DATE [MM-DD-YYYY]: ")
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == date:
            print(f"Current: In {entry['sign_in']}, Out {entry['sign_out']}, Hours {entry['hours']}")
            
            new_signin = input("New Sign-In [MM-DD-YYYY HH:MM:SS] or Press Enter to skip: ")
            if new_signin:
                try:
                    datetime.strptime(new_signin, "%m-%d-%Y %H:%M:%S") 
                    entry["sign_in"] = new_signin
                except ValueError:
                    print("Invalid format!")
            
            new_signout = input("New Sign-Out [MM-DD-YYYY HH:MM:SS] or Press Enter to skip: ")
            if new_signout:
                try:
                    datetime.strptime(new_signout, "%m-%d-%Y %H:%M:%S")  
                    entry["sign_out"] = new_signout
                except ValueError:
                    print("Invalid format!")


            if entry["sign_in"] and entry["sign_out"]:
                try:
                    in_time = datetime.strptime(entry["sign_in"], "%m-%d-%Y %H:%M:%S")
                    out_time = datetime.strptime(entry["sign_out"], "%m-%d-%Y %H:%M:%S")
                    if out_time > in_time:
                        hours = (out_time - in_time).total_seconds() / 3600 # May 3600 seconds sa isang oras 
                        entry["hours"] = round(hours, 2)
                        print(f"Updated hours: {entry['hours']}")
                    else:
                        print("Out time must be after in time.")
                except ValueError:
                    print("Invalid time format!")
            
            save_data(attendance_file, attendance)
            print("Updated!")
            return
    
    print("Entry not found.")

# Payroll Generation
def generate_payroll():
    # HR Password Check
    password = input("Enter HR Password: ")
    if password != hr_pass:
        print("Access denied! For HR only!")
        return

    month = input("Enter Month (MM-YYYY): ")
    
    # Load data
    employees = load_data(employee_file)
    attendance = load_data(attendance_file)
    
    payroll_summary = []

    print("\n--- Generating Payroll ---")

    # Loop through each employee
    for emp in employees:
        emp_id = emp["emp_id"]
        rate = emp["rate"]
        
        regular_hours = 0
        overtime_hours = 0
        
        has_attendance = False
        # Calculate hours from attendance records
        for entry in attendance:
            if entry["emp_id"] == emp_id:
                entry_date = entry["date"]
                # Check if entry matches the month and year
                if entry_date[:2] == month[:2] and entry_date[6:] == month[3:]:
                    has_attendance = True
                    hours = entry["hours"]
                    # Separate overtime hours (assuming > 8 hours is overtime)
                    if hours > 8:
                        regular_hours += 8
                        overtime_hours += (hours - 8)
                    else:
                        regular_hours += hours
        
        if not has_attendance:
            continue

        # Calculate Gross Pay
        gross_pay = (regular_hours * rate) + (overtime_hours * rate * 1.5)
        
        print(f"\nEmployee: {emp['name']} (ID: {emp_id})")
        try:
            # Input Allowances and Deductions
            allowance = float(input("Enter Allowances: ") or 0)
            deduction = float(input("Enter Deductions: ") or 0)
        except ValueError:
            print("Invalid input, setting to 0")
            allowance = 0
            deduction = 0
            
        # Calculate Net Pay
        net_pay = gross_pay + allowance - deduction
        
        payroll_summary.append({
            "id": emp_id,
            "name": emp["name"],
            "reg_hrs": regular_hours,
            "ot_hrs": overtime_hours,
            "gross": gross_pay,
            "net": net_pay
        })

        # Generate Payslip
        print(f"\n--- Payslip for {emp['name']} ---")
        print(f"Period: {month}")
        print(f"Regular Hours: {regular_hours:.2f} hrs @ {rate}/hr")
        print(f"Overtime Hours: {overtime_hours:.2f} hrs @ {rate * 1.5}/hr")
        print(f"Gross Pay: {gross_pay:.2f}")
        print(f"Allowances: {allowance:.2f}")
        print(f"Deductions: {deduction:.2f}")
        print(f"Net Pay: {net_pay:.2f}")
        print("-----------------------------------")

    # Generate Monthly Payroll Summary
    print(f"\n--- Payroll Summary for {month} ---")
    print(f"{'ID':<5} {'Name':<20} {'Reg Hrs':<10} {'OT Hrs':<10} {'Gross':<10} {'Net Pay':<10}")
    for p in payroll_summary:
        print(f"{p['id']:<5} {p['name']:<20} {p['reg_hrs']:<10.2f} {p['ot_hrs']:<10.2f} {p['gross']:<10.2f} {p['net']:<10.2f}")


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
6. Edit Attendance (HR Only!!)
7. Generate Payroll (HR Only!!)
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
        elif choice == 6:
            edit_attendance()
        elif choice == 7:
            generate_payroll()
        else:
            print("Invalid Input!")
        
menu()



from models import Employee
from utils.data_handler import load_data, save_data, get_next_employee_id
from config import EMPLOYEE_FILE


def register_employee():
    """Register a new employee"""
    employees = load_data(EMPLOYEE_FILE)
    emp_id = get_next_employee_id(employees)
    
    print("\n--- Register New Employee ---")
    name = input("Name: ")
    role = input("Role: ")
    dept = input("Department: ")
    
    try:
        rate = float(input("Hourly Rate: "))
    except ValueError:
        print("Invalid rate! Registration cancelled.")
        return
    
    contact = input("Contact: ")
    
    emp = Employee(emp_id, name, role, dept, rate, contact)
    employees.append(emp.to_dict())
    
    save_data(EMPLOYEE_FILE, employees)
    print(f"Employee registered successfully! ID: {emp_id}")


def edit_employee():
    """Edit an existing employee's information"""
    employees = load_data(EMPLOYEE_FILE)
    
    try:
        emp_id = int(input("Enter employee ID to edit: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    for emp in employees:
        if emp["emp_id"] == emp_id:
            print(f"\nEditing Employee: {emp['name']}")
            emp["name"] = input("New Name: ")
            emp["role"] = input("New Role: ")
            emp["dept"] = input("New Department: ")
            
            try:
                emp["rate"] = float(input("New Hourly Rate: "))
            except ValueError:
                print("Invalid rate! Keeping old rate.")
            
            emp["contact"] = input("New Contact: ")
            
            save_data(EMPLOYEE_FILE, employees)
            print("Employee successfully updated!")
            return
    
    print("Employee not found!")


def delete_employee():
    """Delete an employee from the system"""
    employees = load_data(EMPLOYEE_FILE)
    
    try:
        emp_id = int(input("Enter employee ID to delete: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    updated_employees = [emp for emp in employees if emp["emp_id"] != emp_id]
    
    if len(updated_employees) == len(employees):
        print("Employee not found!")
        return
    
    save_data(EMPLOYEE_FILE, updated_employees)
    print("Employee successfully removed!")
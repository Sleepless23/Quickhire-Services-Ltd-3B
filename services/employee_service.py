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
    
def list_employees():
    """Display all employees in a formatted table"""
    employees = load_data(EMPLOYEE_FILE)
    
    if not employees:
        print("\nNo employees found in the system.")
        return
    
    print("\n" + "="*90)
    print("                         QuickHire-Services-Ltd. Employees List")
    print("="*90)
    print(f"{'ID':<5} {'Name':<20} {'Role':<15} {'Department':<15} {'Rate':<10} {'Contact':<15}")
    print("-"*90)
    
    for emp in employees:
        print(f"{emp['emp_id']:<5} {emp['name']:<20} {emp['role']:<15} "
              f"{emp['dept']:<15} ${emp['rate']:<9.2f} {emp['contact']:<15}")
    
    print("="*90)
    print(f"Total Employees: {len(employees)}")
    print()
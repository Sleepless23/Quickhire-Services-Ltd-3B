from models import Employee
from utils.data_handler import load_data, save_data, get_next_employee_id
from utils.select_handler import select_from_list
from config import EMPLOYEE_FILE, DEPARTMENTS


def register_employee():
    """Register a new employee using selection menus."""
    employees = load_data(EMPLOYEE_FILE)
    emp_id = get_next_employee_id(employees)

    print("\n--- Register New Employee ---")
    name = input("Name: ")

    # 1. Choose Department
    department = select_from_list("Select Department", list(DEPARTMENTS.keys()))
    if department is None:
        return

    # 2. Choose Role based on Department
    role = select_from_list(f"Select Role for {department}", DEPARTMENTS[department])
    if role is None:
        return

    # Rate Input
    try:
        rate = float(input("Hourly Rate: "))
    except ValueError:
        print("Invalid rate! Registration cancelled.")
        return

    contact = input("Contact: ")

    emp = Employee(emp_id, name, role, department, rate, contact)
    employees.append(emp.to_dict())

    save_data(EMPLOYEE_FILE, employees)
    print(f"Employee registered successfully! ID: {emp_id}")


def edit_employee():
    """Edit an employee with preview, selection, and confirmation."""
    employees = load_data(EMPLOYEE_FILE)

    try:
        emp_id = int(input("Enter employee ID to edit: "))
    except ValueError:
        print("Invalid Employee ID!")
        return

    for emp in employees:
        if emp["emp_id"] == emp_id:

            print("\n--- Current Employee Information ---")
            print(f"Name       : {emp['name']}")
            print(f"Role       : {emp['role']}")
            print(f"Department : {emp['dept']}")
            print(f"Rate       : {emp['rate']}")
            print(f"Contact    : {emp['contact']}")
            print("-" * 40)

            new_name = edit_field("New Name", emp["name"])

            # Select new department (or keep old)
            print("\nPress Enter to keep the current department.")
            dept_choice = input("Change department? (y/n): ").lower()

            if dept_choice == 'y':
                new_dept = select_from_list("Select Department", list(DEPARTMENTS.keys()))
                if new_dept is None:
                    return
                new_role = select_from_list(f"Select Role for {new_dept}", DEPARTMENTS[new_dept])
            else:
                new_dept = emp["dept"]
                new_role = emp["role"]

            new_rate = edit_field("New Hourly Rate", emp["rate"], numeric=True)
            new_contact = edit_field("New Contact", emp["contact"])

            print("\n--- Confirm Changes ---")
            print(f"Name       : {new_name}")
            print(f"Department : {new_dept}")
            print(f"Role       : {new_role}")
            print(f"Rate       : {new_rate}")
            print(f"Contact    : {new_contact}")
            confirm = input("Save changes? (y/n): ")

            if confirm.lower() != "y":
                print("Changes canceled.")
                return

            # Save
            emp["name"] = new_name
            emp["dept"] = new_dept
            emp["role"] = new_role
            emp["rate"] = new_rate
            emp["contact"] = new_contact

            save_data(EMPLOYEE_FILE, employees)
            print("Employee updated successfully!")
            return

    print("Employee not found!")



def delete_employee():
    """Delete an employee from the system with confirmation"""
    employees = load_data(EMPLOYEE_FILE)

    try:
        emp_id = int(input("Enter employee ID to delete: "))
    except ValueError:
        print("Invalid Employee ID!")
        return

    # Find the employee first
    employee = None
    for emp in employees:
        if emp["emp_id"] == emp_id:
            employee = emp
            break

    if not employee:
        print("Employee not found!")
        return

    # Show employee details
    print("\nEmployee found:")
    print(f"Name       : {employee['name']}")
    print(f"Department : {employee['dept']}")
    print(f"Role       : {employee['role']}")
    print(f"Rate/hr    : ₱{employee['rate']:.2f}")

    # Confirm deletion
    confirm = input("\nAre you sure you want to DELETE this employee? (yes/no): ").strip().lower()

    if confirm not in ["yes", "y"]:
        print("Deletion cancelled.")
        return

    # Proceed with deletion
    updated_employees = [emp for emp in employees if emp["emp_id"] != emp_id]
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
              f"{emp['dept']:<15} ₱{emp['rate']:<9.2f} {emp['contact']:<15}")
    
    print("="*90)
    print(f"Total Employees: {len(employees)}")
    print()
    

def edit_field(label, old_value, *, numeric=False):

    user_input = input(f"{label} [{old_value}]: ").strip()

    # Keep old value if input is empty
    if user_input == "":
        return old_value

    if numeric:
        try:
            return float(user_input)
        except ValueError:
            print("Invalid number! Keeping old value.")
            return old_value

    return user_input

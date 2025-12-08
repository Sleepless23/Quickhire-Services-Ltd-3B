from services.employee_service import register_employee, edit_employee, delete_employee, list_employees
from services.attendance_service import sign_in, sign_out, edit_attendance
from services.payroll_service import generate_payroll, generate_individual_payslip


def display_menu():
    print("""
===============================
    QuickHire-Services-Ltd.
===============================
              
1. Register Employee
2. Edit Employee
3. Delete Employee
4. List All Employees
5. Sign In
6. Sign Out
7. Edit Attendance (HR Only!)
8. Generate Individual Payslip (HR Only!)
9. Generate Monthly Payroll (HR Only!)
10. Exit
""")


def main():
    """Main application loop"""
    while True:
        display_menu()
        
        try:
            choice = int(input("Select Option: "))
        except ValueError:
            print("Invalid input! Please enter a number.")
            continue
        
        if choice == 1:
            register_employee()
        elif choice == 2:
            edit_employee()
        elif choice == 3:
            delete_employee()
        elif choice == 4:
            list_employees()
        elif choice == 5:
            sign_in()
        elif choice == 6:
            sign_out()
        elif choice == 7:
            edit_attendance()
        elif choice == 8:
            generate_individual_payslip()
        elif choice == 9:
            generate_payroll()
        elif choice == 10:
            print("Thank you for using QuickHire Services!")
            break
        else:
            print("Invalid option! Please select 1-9.")


if __name__ == "__main__":
    main()
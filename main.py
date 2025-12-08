from services.employee_service import register_employee, edit_employee, delete_employee
from services.attendance_service import sign_in, sign_out, edit_attendance
from services.payroll_service import generate_payroll


def display_menu():
    print("""
===============================
    QuickHire-Services-Ltd.
===============================
              
1. Register Employee
2. Edit Employee
3. Delete Employee
4. Sign In
5. Sign Out
6. Edit Attendance (HR Only!)
7. Generate Payroll (HR Only!)
8. Exit
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
            sign_in()
        elif choice == 5:
            sign_out()
        elif choice == 6:
            edit_attendance()
        elif choice == 7:
            generate_payroll()
        elif choice == 8:
            print("Thank you for using QuickHire Services!")
            break
        else:
            print("Invalid option! Please select 1-8.")


if __name__ == "__main__":
    main()
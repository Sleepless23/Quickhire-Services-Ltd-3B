from utils.data_handler import load_data
from config import (EMPLOYEE_FILE, ATTENDANCE_FILE, HR_PASSWORD, 
                   REGULAR_HOURS_PER_DAY, OVERTIME_MULTIPLIER)


def generate_individual_payslip():
    """Generate payslip for a single employee"""
    password = input("Enter HR Password: ")
    if password != HR_PASSWORD:
        print("Access denied! For HR only!")
        return
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    month = input("Enter Month (MM-YYYY): ")
    
    # Validate month format
    if len(month) != 7 or month[2] != '-':
        print("Invalid format! Use MM-YYYY")
        return
    
    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    
    # Find the employee
    employee = None
    for emp in employees:
        if emp["emp_id"] == emp_id:
            employee = emp
            break
    
    if not employee:
        print("Employee not found!")
        return
    
    # Calculate hours
    regular_hours = 0
    overtime_hours = 0
    has_attendance = False
    
    for entry in attendance:
        if entry["emp_id"] == emp_id:
            entry_date = entry["date"]
            # Check if entry matches the month and year
            if entry_date[:2] == month[:2] and entry_date[6:] == month[3:]:
                has_attendance = True
                hours = entry["hours"]
                
                if hours > REGULAR_HOURS_PER_DAY:
                    regular_hours += REGULAR_HOURS_PER_DAY
                    overtime_hours += (hours - REGULAR_HOURS_PER_DAY)
                else:
                    regular_hours += hours
    
    if not has_attendance:
        print(f"No attendance records found for {employee['name']} in {month}")
        return
    
    rate = employee["rate"]
    gross_pay = (regular_hours * rate) + (overtime_hours * rate * OVERTIME_MULTIPLIER)
    
    print(f"\n--- Payslip Details for {employee['name']} ---")
    
    try:
        allowance = float(input("Enter Allowances: ") or 0)
        deduction = float(input("Enter Deductions: ") or 0)
    except ValueError:
        print("Invalid input, setting to 0")
        allowance = 0
        deduction = 0
    
    # Add Allowance
    gross_pay += allowance
    
    net_pay = gross_pay + allowance - deduction
    
    # Print payslip
    _print_payslip(employee, month, regular_hours, overtime_hours, rate,
                   gross_pay, allowance, deduction, net_pay)
    
def generate_payroll():
    """Generate payroll for a given month (HR only)"""
    password = input("Enter HR Password: ")
    if password != HR_PASSWORD:
        print("Access denied! For HR only!")
        return
    
    month = input("Enter Month (MM-YYYY): ")
    
    # Validate month format
    if len(month) != 7 or month[2] != '-':
        print("Invalid format! Use MM-YYYY")
        return
    
    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    
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
                    
                    if hours > REGULAR_HOURS_PER_DAY:
                        regular_hours += REGULAR_HOURS_PER_DAY
                        overtime_hours += (hours - REGULAR_HOURS_PER_DAY)
                    else:
                        regular_hours += hours
        
        # Skip employees with no attendance
        if not has_attendance:
            continue
        
        # Calculate Gross Pay
        gross_pay = (regular_hours * rate) + (overtime_hours * rate * OVERTIME_MULTIPLIER)
        
        print(f"\nEmployee: {emp['name']} (ID: {emp_id})")
        
        try:
            allowance = float(input("Enter Allowances: ") or 0)
            deduction = float(input("Enter Deductions: ") or 0)
        except ValueError:
            print("Invalid input, setting to 0")
            allowance = 0
            deduction = 0
        
        # Add Allowance
        gross_pay += allowance
        # Calculate Net Pay
        net_pay = gross_pay - deduction
        
        payroll_summary.append({
            "id": emp_id,
            "name": emp["name"],
            "rate": rate,
            "reg_hrs": regular_hours,
            "ot_hrs": overtime_hours,
            "allowance": allowance,
            "deduction": deduction,
            "gross": gross_pay,
            "net": net_pay
        })
        
        # Generate Payslip - Comment ko muna to ha
        # _print_payslip(emp, month, regular_hours, overtime_hours, rate, 
        #               gross_pay, allowance, deduction, net_pay)
    
    # Generate Monthly Payroll Summary
    _print_payroll_summary(month, payroll_summary)


def _print_payslip(emp, month, regular_hours, overtime_hours, rate, 
                   gross_pay, allowance, deduction, net_pay):
    """Print individual payslip"""
    regular_pay = regular_hours * rate
    overtime_pay = overtime_hours * rate * OVERTIME_MULTIPLIER
    
    print("\n" + "="*50)
    print(f"         PAYSLIP FOR {emp['name'].upper()}")
    print("="*50)
    print(f"Employee ID    : {emp['emp_id']}")
    print(f"Department     : {emp['dept']}")
    print(f"Role           : {emp['role']}")
    print(f"Period         : {month}")
    print("-"*50)
    print("HOURS WORKED")
    print(f"Regular Hours  : {regular_hours:>8.2f} hrs @ ₱{rate:.2f}/hr")
    print(f"Overtime Hours : {overtime_hours:>8.2f} hrs @ ₱{rate * OVERTIME_MULTIPLIER:.2f}/hr")
    print("-"*50)
    print("EARNINGS")
    print(f"Regular Pay    : ₱{regular_pay:>8.2f}")
    print(f"Overtime Pay   : ₱{overtime_pay:>8.2f}")
    print(f"Allowances     : ₱{allowance:>8.2f}")
    print("-"*50)
    print(f"Gross Pay      :   ₱{gross_pay:>8.2f}")
    print(f"Deductions     : - ₱{deduction:>8.2f}")
    print("="*50)
    print(f"NET PAY        : ₱{net_pay:>8.2f}")
    print("="*50)
    print()


def _print_payroll_summary(month, payroll_summary):
    """Print payroll summary table with allowances, rate, deductions, totals"""

    print("\n" + "="*120)
    print(f"{'                                          PAYROLL SUMMARY FOR':<25} {month}")
    print("="*120)
    
    # Table Header
    print(
        f"{'ID':<5} {'Name':<20} {'Rate/hr':<10} {'Reg Hrs':<10} {'OT Hrs':<10} "
        f"{'Allowance':<12} {'Gross':<12} {'Deduction':<12} {'Net Pay':<12}"
    )
    print("-"*120)

    # Totals
    total_reg = 0
    total_ot = 0
    total_allowance = 0
    total_gross = 0
    total_deduction = 0
    total_net = 0

    for p in payroll_summary:

        # Extract values (allowance & deduction must be stored!)
        rate = p.get("rate", 0)
        allowance = p.get("allowance", 0)
        deduction = p.get("deduction", 0)

        print(
            f"{p['id']:<5} {p['name']:<20} ₱{rate:<9.2f} "
            f"{p['reg_hrs']:<10.2f} {p['ot_hrs']:<10.2f} "
            f"₱{allowance:<11.2f} ₱{p['gross']:<11.2f} "
            f"₱{deduction:<11.2f} ₱{p['net']:<11.2f}"
        )

        total_reg += p["reg_hrs"]
        total_ot += p["ot_hrs"]
        total_allowance += allowance
        total_gross += p["gross"]
        total_deduction += deduction
        total_net += p["net"]

    print("="*120)
    print(
        f"{'TOTAL':<25} "
        f"{'':<10} "
        f"{total_reg:<10.2f} {total_ot:<10.2f} "
        f"₱{total_allowance:<11.2f} "
        f"₱{total_gross:<11.2f} "
        f"₱{total_deduction:<11.2f} "
        f"₱{total_net:<11.2f}"
    )
    print("="*120)
    print()

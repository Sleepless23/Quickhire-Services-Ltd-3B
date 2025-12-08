from utils.data_handler import load_data
from config import (EMPLOYEE_FILE, ATTENDANCE_FILE, HR_PASSWORD, 
                   REGULAR_HOURS_PER_DAY, OVERTIME_MULTIPLIER)


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
        _print_payslip(emp, month, regular_hours, overtime_hours, rate, 
                      gross_pay, allowance, deduction, net_pay)
    
    # Generate Monthly Payroll Summary
    _print_payroll_summary(month, payroll_summary)


def _print_payslip(emp, month, regular_hours, overtime_hours, rate, 
                   gross_pay, allowance, deduction, net_pay):
    """Print individual payslip"""
    print(f"\n--- Payslip for {emp['name']} ---")
    print(f"Period: {month}")
    print(f"Regular Hours: {regular_hours:.2f} hrs @ ${rate}/hr")
    print(f"Overtime Hours: {overtime_hours:.2f} hrs @ ${rate * OVERTIME_MULTIPLIER}/hr")
    print(f"Gross Pay: ${gross_pay:.2f}")
    print(f"Allowances: ${allowance:.2f}")
    print(f"Deductions: ${deduction:.2f}")
    print(f"Net Pay: ${net_pay:.2f}")
    print("-----------------------------------")


def _print_payroll_summary(month, payroll_summary):
    """Print payroll summary table"""
    print(f"\n--- Payroll Summary for {month} ---")
    print(f"{'ID':<5} {'Name':<20} {'Reg Hrs':<10} {'OT Hrs':<10} {'Gross':<12} {'Net Pay':<12}")
    print("-" * 75)
    
    for p in payroll_summary:
        print(f"{p['id']:<5} {p['name']:<20} {p['reg_hrs']:<10.2f} "
              f"{p['ot_hrs']:<10.2f} ${p['gross']:<11.2f} ${p['net']:<11.2f}")
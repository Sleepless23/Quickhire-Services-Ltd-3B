import json
from config import RED, GREEN, BOLD, RESET
from utils.data_handler import load_data
from utils.security import verify_hr_access
from config import (EMPLOYEE_FILE, ATTENDANCE_FILE, HR_PASSWORD, 
                   REGULAR_HOURS_PER_DAY, OVERTIME_MULTIPLIER)


def prepare_payroll_inputs():
    
    if not verify_hr_access():
        return
    """Assign allowances and deductions to each employee for a specific month"""
    employees = load_data(EMPLOYEE_FILE)
    month = input("Enter Month-Year (MM-YYYY): ")

    payroll_inputs = []
    for emp in employees:
        print(f"\nEmployee: {emp['name']} (ID: {emp['emp_id']})")
        try:
            allowance = float(input("Enter Allowances: ") or 0)
            deduction = float(input("Enter Deductions: ") or 0)
        except ValueError:
            print("Invalid input, setting to 0")
            allowance = 0
            deduction = 0
        
        payroll_inputs.append({
            "emp_id": emp["emp_id"],
            "month": month,
            "allowance": allowance,
            "deduction": deduction
        })

    # Save to JSON for later use in payroll generation
    with open("payroll_inputs.json", "w") as f:
        json.dump(payroll_inputs, f, indent=4)
    
    print("\nPayroll inputs saved!")
    
    
def generate_individual_payslip():
    
    if not verify_hr_access():
        return
    """Generate payslip for a single employee using prepared payroll inputs"""
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    month = input("Enter Month-Year (MM-YYYY): ")
    
    # Validate month format
    if len(month) != 7 or month[2] != '-':
        print("Invalid format! Use MM-YYYY")
        return
    
    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    
    # Find the employee
    employee = next((e for e in employees if e["emp_id"] == emp_id), None)
    if not employee:
        print("Employee not found!")
        return

    # Load allowances/deductions from prepared inputs
    try:
        with open("payroll_inputs.json", "r") as f:
            payroll_inputs = json.load(f)
    except FileNotFoundError:
        print("Payroll inputs not found! Please prepare payroll first.")
        return
    
    payroll_input = next((x for x in payroll_inputs if x["emp_id"] == emp_id and x["month"] == month), {})
    pay_data = calculate_pay(employee, attendance, payroll_input, month)
    if not pay_data:
        print(f"No attendance records found for {employee['name']} in {month}")
        return

    _print_payslip(employee, month, pay_data["reg_hours"], pay_data["ot_hours"], pay_data["rate"],
                   pay_data["gross"], pay_data["allowance"], pay_data["deduction"], pay_data["net"])

    
def generate_payroll():
    
    if not verify_hr_access():
        return
    """Generate payroll automatically using prepared inputs"""
    month = input("Enter Month-Year (MM-YYYY): ")
    
    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    
    # Load previously prepared allowances/deductions
    try:
        with open("payroll_inputs.json", "r") as f:
            payroll_inputs = json.load(f)
    except FileNotFoundError:
        print("Payroll inputs not found! Please prepare payroll first.")
        return
    
    payroll_summary = []
    
    for emp in employees:
        payroll_input = next((x for x in payroll_inputs if x["emp_id"] == emp["emp_id"] and x["month"] == month), {})
        pay_data = calculate_pay(emp, attendance, payroll_input, month)
        if not pay_data:
            continue  # skip employees with no attendance

        payroll_summary.append({
            "id": emp["emp_id"],
            "name": emp["name"],
            "rate": pay_data["rate"],
            "reg_hrs": pay_data["reg_hours"],
            "ot_hrs": pay_data["ot_hours"],
            "allowance": pay_data["allowance"],
            "deduction": pay_data["deduction"],
            "gross": pay_data["gross"],
            "net": pay_data["net"]
        })

    _print_payroll_summary(month, payroll_summary)
    

def _print_payslip(emp, month, regular_hours, overtime_hours, rate, 
                   gross_pay, allowance, deduction, net_pay):
    """Print individual payslip"""
    regular_pay = regular_hours * rate
    overtime_pay = overtime_hours * rate * OVERTIME_MULTIPLIER
    
    print("\n" + "="*50)
    print(f"         {BOLD}PAYSLIP FOR {emp['name'].upper()}{RESET}")
    print("="*50)
    print(f"Employee ID    : {emp['emp_id']}")
    print(f"Department     : {emp['dept']}")
    print(f"Role           : {emp['role']}")
    print(f"Period         : {month}")
    print("-"*50)
    print(f"{BOLD}HOURS WORKED{RESET}")
    print(f"Regular Hours  : {regular_hours:>8.2f} hrs @ ₱{rate:.2f}/hr")
    print(f"Overtime Hours : {overtime_hours:>8.2f} hrs @ ₱{rate * OVERTIME_MULTIPLIER:.2f}/hr")
    print("-"*50)
    print(f"{BOLD}EARNINGS{RESET}")
    print(f"Regular Pay    : ₱{regular_pay:>8.2f}")
    print(f"Overtime Pay   : ₱{overtime_pay:>8.2f}")
    print(f"Allowances     : ₱{allowance:>8.2f}")
    print("-"*50)
    print(f"Gross Pay      :   ₱{gross_pay:>8.2f}")
    print(f"Deductions     : {RED}- ₱{deduction:>8.2f}{RESET}")
    print("="*50)
    print(f"NET PAY        : {GREEN} ₱{net_pay:>8.2f}{RESET}")
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

        # Extract values
        rate = p.get("rate", 0)
        allowance = p.get("allowance", 0)
        deduction = p.get("deduction", 0)

        print(
            f"{p['id']:<5} {p['name']:<20} ₱{rate:<9.2f} "
            f"{p['reg_hrs']:<10.2f} {p['ot_hrs']:<10.2f} "
            f"₱{allowance:<11.2f} ₱{p['gross']:<11.2f} "
            f"- ₱{deduction:<11.2f} ₱{p['net']:<11.2f}"
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
        f"{'':<11} "
        f"{total_reg:<10.2f} {total_ot:<10.2f} "
        f"₱{total_allowance:<11.2f} "
        f"₱{total_gross:<11.2f} "
        f" ₱{total_deduction:<11.2f} "
        f"₱{total_net:<11.2f}"
    )
    print("="*120)
    print()

def calculate_pay(emp, attendance, payroll_input, month):

    emp_id = emp["emp_id"]
    
    regular_hours = 0
    overtime_hours = 0
    has_attendance = False

    for entry in attendance:
        if entry["emp_id"] == emp_id:
            entry_date = entry["date"]
            if entry_date[:2] == month[:2] and entry_date[6:] == month[3:]:
                has_attendance = True
                hours = entry["hours"]
                if hours > REGULAR_HOURS_PER_DAY:
                    regular_hours += REGULAR_HOURS_PER_DAY
                    overtime_hours += hours - REGULAR_HOURS_PER_DAY
                else:
                    regular_hours += hours

    if not has_attendance:
        return None  # no attendance for this month

    rate = emp["rate"]
    allowance = payroll_input.get("allowance", 0)
    deduction = payroll_input.get("deduction", 0)
    
    gross_pay = (regular_hours * rate) + (overtime_hours * rate * OVERTIME_MULTIPLIER) + allowance
    net_pay = gross_pay - deduction

    return {
        "emp": emp,
        "reg_hours": regular_hours,
        "ot_hours": overtime_hours,
        "rate": rate,
        "allowance": allowance,
        "deduction": deduction,
        "gross": gross_pay,
        "net": net_pay
    }
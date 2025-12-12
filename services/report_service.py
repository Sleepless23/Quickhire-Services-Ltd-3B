import json
from datetime import datetime
from utils.data_handler import load_data
from utils.export_helpers import save_csv, save_pdf, save_text
from utils.security import verify_hr_access
from config import (EMPLOYEE_FILE, ATTENDANCE_FILE, RED, GREEN, BOLD, RESET,
                    DATE_FORMAT, DATETIME_FORMAT,
                    REGULAR_HOURS_PER_DAY, OVERTIME_MULTIPLIER)

REPORT_DIR = "reports/"


def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except Exception:
        return None


def _load_payroll_inputs():
    try:
        with open("payroll_inputs.json", "r") as f:
            return json.load(f)
    except Exception:
        return []


def export_monthly_payroll():
    """HR-only: export a payroll CSV for a given month (MM-YYYY)."""
    if not verify_hr_access():
        return
    month = input("Enter Month-Year (MM-YYYY): ").strip()
    if len(month) != 7 or month[2] != '-':
        print("Invalid format. Use MM-YYYY.")
        return

    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    payroll_inputs = _load_payroll_inputs()

    rows = []
    fieldnames = ["id", "name", "department", "role", "rate", "regular_hours", "overtime_hours", "allowance", "deduction", "gross", "net"]

    for emp in employees:
        emp_id = emp["emp_id"]
        rate = float(emp.get("rate", 0))
        reg_hours = 0.0
        ot_hours = 0.0
        has_att = False

        for entry in attendance:
            if entry.get("emp_id") != emp_id:
                continue
            entry_date = entry.get("date", "")
            if len(entry_date) == 10 and entry_date[:2] == month[:2] and entry_date[6:] == month[3:]:
                has_att = True
                hours = float(entry.get("hours", 0) or 0)
                if hours > REGULAR_HOURS_PER_DAY:
                    reg_hours += REGULAR_HOURS_PER_DAY
                    ot_hours += (hours - REGULAR_HOURS_PER_DAY)
                else:
                    reg_hours += hours

        # find prepared inputs for this emp/month
        p_input = next((p for p in payroll_inputs if p.get("emp_id") == emp_id and p.get("month") == month), {})
        allowance = float(p_input.get("allowance", 0))
        deduction = float(p_input.get("deduction", 0))

        gross = (reg_hours * rate) + (ot_hours * rate * OVERTIME_MULTIPLIER) + allowance
        net = gross - deduction

        rows.append({
            "id": emp_id,
            "name": emp.get("name"),
            "department": emp.get("dept"),
            "role": emp.get("role"),
            "rate": f"{rate:.2f}",
            "regular_hours": f"{reg_hours:.2f}",
            "overtime_hours": f"{ot_hours:.2f}",
            "allowance": f"{allowance:.2f}",
            "deduction": f"{deduction:.2f}",
            "gross": f"{gross:.2f}",
            "net": f"{net:.2f}"
        })

    # Display preview
    _print_monthly_payroll_preview(month, rows)
    
    # Ask for export format
    export_choice = input("\nExport as (1) CSV, (2) PDF, or (3) Skip: ").strip()
    
    if export_choice == "1":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"monthly_payroll_{month.replace('-', '')}_{timestamp}.csv"
        path = save_csv(default_filename, fieldnames, rows, use_dialog=True)
        
        if path:
            print(f"{GREEN}✓ Monthly payroll CSV exported: {path}{RESET}")
        return path

    elif export_choice == "2":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"monthly_payroll_{month.replace('-', '')}_{timestamp}.pdf"
        lines = _build_monthly_payroll_lines(month, rows)
        path = save_pdf(default_filename, f"Monthly Payroll Report - {month}", lines, use_dialog=True)
        
        if path:
            print(f"{GREEN}✓ Monthly payroll PDF exported: {path}{RESET}")
        return path
    else:
        print("Report generation complete (not exported)")


def export_individual_attendance():
    """Export a single employee's attendance history to CSV or PDF."""
    if not verify_hr_access():
        return
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID.")
        return

    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    
    # Find employee
    employee = next((e for e in employees if e["emp_id"] == emp_id), None)
    if not employee:
        print("Employee not found!")
        return
    
    rows = []
    fieldnames = ["emp_id", "emp_name", "date", "sign_in", "sign_out", "hours"]

    filtered = [a for a in attendance if a.get("emp_id") == emp_id]
    # sort by date
    filtered.sort(key=lambda x: _parse_date(x.get("date", "")) or datetime.min)

    for e in filtered:
        rows.append({
            "emp_id": emp_id,
            "emp_name": employee["name"],
            "date": e.get("date", ""),
            "sign_in": e.get("sign_in") or "N/A",
            "sign_out": e.get("sign_out") or "N/A",
            "hours": f"{float(e.get('hours', 0)):.2f}"
        })

    if not rows:
        print(f"No attendance records found for {employee['name']}")
        return

    # Display preview
    _print_attendance_history_preview(employee, rows)
    
    # Ask for export format
    export_choice = input("\nExport as (1) CSV, (2) PDF, or (3) Skip: ").strip()
    
    if export_choice == "1":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"attendance_history_emp_{emp_id}_{timestamp}.csv"
        path = save_csv(default_filename, fieldnames, rows, use_dialog=True)
        if path:
            print(f"{GREEN}✓ Attendance history exported: {path}{RESET}")
        return path
    elif export_choice == "2":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"attendance_history_emp_{emp_id}_{timestamp}.pdf"
        lines = _build_attendance_history_lines(employee, rows)
        path = save_pdf(default_filename, f"Attendance History - {employee['name']}", lines, use_dialog=True)
        if path:
            print(f"{GREEN}✓ Attendance history exported: {path}{RESET}")
        return path
    else:
        print("Report generation complete (not exported)")


def export_overtime_report():
    """Export overtime occurrences for a specified month (MM-YYYY)."""
    if not verify_hr_access():
        return
    month = input("Enter Month-Year (MM-YYYY): ").strip()
    if len(month) != 7 or month[2] != '-':
        print("Invalid format. Use MM-YYYY.")
        return

    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    rows = []
    fieldnames = ["emp_id", "name", "date", "hours", "overtime_hours"]

    for entry in attendance:
        d = entry.get("date", "")
        if len(d) == 10 and d[:2] == month[:2] and d[6:] == month[3:]:
            hours = float(entry.get("hours", 0) or 0)
            if hours > REGULAR_HOURS_PER_DAY:
                ot = round(hours - REGULAR_HOURS_PER_DAY, 2)
                emp = next((e for e in employees if e["emp_id"] == entry["emp_id"]), None)
                name = emp["name"] if emp else f"Employee {entry['emp_id']}"
                rows.append({
                    "emp_id": entry["emp_id"],
                    "name": name,
                    "date": d,
                    "hours": f"{hours:.2f}",
                    "overtime_hours": f"{ot:.2f}"
                })

    if not rows:
        print(f"No overtime records found for {month}")
        return

    # Display preview
    _print_overtime_report_preview(month, rows)
    
    # Ask for export format
    export_choice = input("\nExport as (1) CSV, (2) PDF, or (3) Skip: ").strip()
    
    if export_choice == "1":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"overtime_report_{month.replace('-', '')}_{timestamp}.csv"
        path = save_csv(default_filename, fieldnames, rows, use_dialog=True)
        if path:    
            print(f"{GREEN}✓ Overtime report exported: {path}{RESET}")
        return path
    elif export_choice == "2":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"overtime_report_{month.replace('-', '')}_{timestamp}.pdf"
        lines = _build_overtime_report_lines(month, rows)
        path = save_pdf(default_filename,  f"Overtime Report - {month}", lines, use_dialog=True)
        if path:
            print(f"{GREEN}✓ Overtime report exported: {path}{RESET}")
        return path
    else:
        print("Report generation complete (not exported)")


def export_daily_attendance_summary():
    """Export daily attendance summary for a specified date (MM-DD-YYYY) - includes all employees."""
    if not verify_hr_access():
        return
    date_str = input("Enter Date (MM-DD-YYYY): ").strip()
    if len(date_str) != 10 or date_str[2] != '-' or date_str[5] != '-':
        print("Invalid date format. Use (MM-DD-YYYY).")
        return

    attendance = load_data(ATTENDANCE_FILE)
    employees = load_data(EMPLOYEE_FILE)

    rows = []
    fieldnames = ["emp_id", "name", "sign_in", "sign_out", "hours"]

    # Include ALL employees, not just those with attendance
    for emp in employees:
        emp_id = emp["emp_id"]
        entry = next((a for a in attendance if a.get("emp_id") == emp_id and a.get("date") == date_str), None)
        
        if entry:
            sign_in = entry.get("sign_in") or "Absent"
            sign_out = entry.get("sign_out") or "Absent"
            hours = f"{float(entry.get('hours', 0)):.2f}"
        else:
            sign_in = "Absent"
            sign_out = "Absent"
            hours = "0.00"
        
        rows.append({
            "emp_id": emp_id,
            "name": emp["name"],
            "sign_in": sign_in,
            "sign_out": sign_out,
            "hours": hours
        })

    # Display preview
    _print_daily_attendance_preview(date_str, rows)
    
    # Ask for export format
    export_choice = input("\nExport as (1) CSV, (2) PDF, or (3) Skip: ").strip()
    
    if export_choice == "1":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"daily_summary_{date_str.replace('-', '')}_{timestamp}.csv"
        path = save_csv(default_filename, fieldnames, rows, use_dialog=True)
        if path:
            print(f"{GREEN}✓ Daily attendance summary exported: {path}{RESET}")
        return path
    elif export_choice == "2":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"daily_summary_{date_str.replace('-', '')}_{timestamp}.pdf"
        lines = _build_daily_attendance_lines(date_str, rows)
        path = save_pdf(default_filename, f"Daily Attendance Summary - {date_str}", lines, use_dialog=True)
        if path:
            print(f"{GREEN}✓ Daily attendance summary exported: {path}{RESET}")
        return path
    else:
        print("Report generation complete (not exported)")

# ========== PREVIEW PRINT FUNCTIONS ==========

def _print_monthly_payroll_preview(month, rows):
    """Display monthly payroll preview on screen"""
    print("\n" + "="*120)
    print(f"{BOLD}MONTHLY PAYROLL REPORT - {month}{RESET}")
    print("="*120)
    print(f"{'ID':<5} {'Name':<20} {'Dept':<15} {'Rate':<10} {'Reg Hrs':<10} {'OT Hrs':<10} {'Allowance':<12} {'Gross':<12} {'Net':<12}")
    print("-"*120)
    
    total_gross = 0
    total_net = 0
    
    for r in rows:
        print(f"{r['id']:<5} {r['name']:<20} {r['department']:<15} ₱{r['rate']:<9} "
              f"{r['regular_hours']:<10} {r['overtime_hours']:<10} ₱{r['allowance']:<11} "
              f"₱{r['gross']:<11} ₱{r['net']:<11}")
        total_gross += float(r['gross'])
        total_net += float(r['net'])
    
    print("="*120)
    print(f"{'TOTAL':<70} ₱{total_gross:<11.2f} ₱{total_net:<11.2f}")
    print("="*120)


def _print_attendance_history_preview(employee, rows):
    """Display attendance history preview on screen"""
    print("\n" + "="*90)
    print(f"{BOLD}ATTENDANCE HISTORY - {employee['name'].upper()} (ID: {employee['emp_id']}){RESET}")
    print("="*90)
    print(f"{'Date':<15} {'Sign In':<15} {'Sign Out':<15} {'Hours':<10}")
    print("-"*90)
    
    total_hours = 0
    for r in rows:
        print(f"{r['date']:<15} {r['sign_in']:<15} {r['sign_out']:<15} {r['hours']:<10}")
        total_hours += float(r['hours'])
    
    print("="*90)
    print(f"Total Hours Worked: {total_hours:.2f}")
    print("="*90)


def _print_overtime_report_preview(month, rows):
    """Display overtime report preview on screen"""
    print("\n" + "="*100)
    print(f"{BOLD}OVERTIME REPORT - {month}{RESET}")
    print("="*100)
    print(f"{'ID':<6} {'Name':<20} {'Date':<15} {'Total Hours':<15} {'Overtime Hours':<15}")
    print("-"*100)
    
    total_ot = 0
    for r in rows:
        print(f"{r['emp_id']:<6} {r['name']:<20} {r['date']:<15} {r['hours']:<15} {r['overtime_hours']:<15}")
        total_ot += float(r['overtime_hours'])
    
    print("="*100)
    print(f"Total Overtime Hours: {total_ot:.2f}")
    print("="*100)


def _print_daily_attendance_preview(date_str, rows):
    """Display daily attendance preview on screen"""
    print("\n" + "="*90)
    print(f"{BOLD}DAILY ATTENDANCE SUMMARY - {date_str}{RESET}")
    print("="*90)
    print(f"{'ID':<6} {'Name':<20} {'Sign In':<15} {'Sign Out':<15} {'Hours':<10}")
    print("-"*90)
    
    present_count = 0
    total_hours = 0
    
    for r in rows:
        print(f"{r['emp_id']:<6} {r['name']:<20} {r['sign_in']:<15} {r['sign_out']:<15} {r['hours']:<10}")
        if r['sign_in'] != "Absent":
            present_count += 1
            total_hours += float(r['hours'])
    
    print("="*90)
    print(f"Employees Present: {present_count}/{len(rows)}")
    print(f"Total Hours: {total_hours:.2f}")
    print("="*90)


# ========== PDF LINE BUILDERS ==========

def _build_monthly_payroll_lines(month, rows):
    """Build lines for monthly payroll PDF with improved spacing"""
    lines = []
    lines.append("")
    lines.append(
        f"{'ID':<6} {'Name':<22} {'Dept':<18} {'Rate':<10} "
        f"{'Reg Hrs':<10} {'OT Hrs':<10} {'Allow':<12} {'Gross':<12} {'Net':<12}"
    )
    lines.append("-" * 120)

    total_gross = 0
    total_net = 0

    for r in rows:
        lines.append(
            f"{r['id']:<6} {r['name']:<22} {r['department']:<18} {r['rate']:<10} "
            f"{r['regular_hours']:<10} {r['overtime_hours']:<10} {r['allowance']:<12} "
            f"{r['gross']:<12} {r['net']:<12}"
        )
        total_gross += float(r['gross'])
        total_net += float(r['net'])

    lines.append("")
    lines.append(f"TOTALS: Gross={total_gross:.2f}, Net={total_net:.2f}")
    return lines



def _build_attendance_history_lines(employee, rows):
    """Build lines for attendance history PDF (fixed spacing)"""
    lines = []
    lines.append("")
    lines.append(f"Employee: {employee['name']} (ID: {employee['emp_id']})")
    lines.append("")
    lines.append(f"{'Date':<18} {'Sign In':<18} {'Sign Out':<18} {'Hours':<10}")
    lines.append("-" * 80)

    total_hours = 0

    for r in rows:
        lines.append(
            f"{r['date']:<18} {r['sign_in']:<18} {r['sign_out']:<18} {r['hours']:<10}"
        )
        total_hours += float(r['hours'])

    lines.append("")
    lines.append(f"Total Hours Worked: {total_hours:.2f}")
    return lines


def _build_overtime_report_lines(month, rows):
    """Build lines for overtime report PDF (fixed spacing)"""
    lines = []
    lines.append("")
    lines.append(
        f"{'ID':<6} {'Name':<22} {'Date':<18} {'Total Hrs':<14} {'OT Hrs':<14}"
    )
    lines.append("-" * 90)

    total_ot = 0

    for r in rows:
        lines.append(
            f"{r['emp_id']:<6} {r['name']:<22} {r['date']:<18} "
            f"{r['hours']:<14} {r['overtime_hours']:<14}"
        )
        total_ot += float(r['overtime_hours'])

    lines.append("")
    lines.append(f"Total Overtime Hours: {total_ot:.2f}")
    return lines


def _build_daily_attendance_lines(date_str, rows):
    """Build lines for daily attendance PDF (fixed spacing)"""
    lines = []
    lines.append("")
    lines.append(
        f"{'ID':<6} {'Name':<22} {'Sign In':<18} {'Sign Out':<18} {'Hours':<10}"
    )
    lines.append("-" * 90)

    present_count = 0
    total_hours = 0

    for r in rows:
        lines.append(
            f"{r['emp_id']:<6} {r['name']:<22} {r['sign_in']:<18} "
            f"{r['sign_out']:<18} {r['hours']:<10}"
        )

        if r['sign_in'] != "Absent":
            present_count += 1
            total_hours += float(r['hours'])

    lines.append("")
    lines.append(f"Employees Present: {present_count}/{len(rows)}")
    lines.append(f"Total Hours: {total_hours:.2f}")
    return lines

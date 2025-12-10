import json
from datetime import datetime
from utils.data_handler import load_data
from utils.export_helpers import save_csv, save_pdf, save_text
from utils.security import verify_hr_access
from config import (EMPLOYEE_FILE, ATTENDANCE_FILE,
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


def export_monthly_payroll_csv():
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

    path = f"{REPORT_DIR}monthly_payroll_{month}.csv"
    save_csv(path, fieldnames, rows)
    print(f"Monthly payroll CSV exported: {path}")
    return path


def export_individual_attendance_csv():
    """Export a single employee's attendance history to CSV."""
    if not verify_hr_access():
        return
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID.")
        return

    attendance = load_data(ATTENDANCE_FILE)
    rows = []
    fieldnames = ["date", "sign_in", "sign_out", "hours"]

    filtered = [a for a in attendance if a.get("emp_id") == emp_id]
    # sort by date
    filtered.sort(key=lambda x: _parse_date(x.get("date", "")) or datetime.min)

    for e in filtered:
        rows.append({
            "date": e.get("date", ""),
            "sign_in": e.get("sign_in") or "",
            "sign_out": e.get("sign_out") or "",
            "hours": f"{float(e.get('hours', 0)):.2f}"
        })

    path = f"{REPORT_DIR}attendance_history_emp_{emp_id}.csv"
    save_csv(path, fieldnames, rows)
    print(f"Attendance history exported: {path}")
    return path


def export_overtime_report_csv():
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

    path = f"{REPORT_DIR}overtime_report_{month}.csv"
    save_csv(path, fieldnames, rows)
    print(f"Overtime report exported: {path}")
    return path


def export_daily_attendance_summary_csv():
    """Export daily attendance summary for a specified date (MM-DD-YYYY)."""
    if not verify_hr_access():
        return
    date_str = input("Enter Date (MM-DD-YYYY): ").strip()
    if len(date_str) != 10:
        print("Invalid date format.")
        return

    attendance = load_data(ATTENDANCE_FILE)
    employees = load_data(EMPLOYEE_FILE)

    rows = []
    fieldnames = ["emp_id", "name", "sign_in", "sign_out", "hours", "status"]

    for entry in attendance:
        if entry.get("date") != date_str:
            continue
        emp = next((e for e in employees if e["emp_id"] == entry["emp_id"]), None)
        name = emp["name"] if emp else f"Employee {entry['emp_id']}"
        sign_in = entry.get("sign_in") or ""
        sign_out = entry.get("sign_out") or ""
        hours = f"{float(entry.get('hours', 0)):.2f}"
        status = "Present" if sign_in else "Absent"
        rows.append({
            "emp_id": entry["emp_id"],
            "name": name,
            "sign_in": sign_in,
            "sign_out": sign_out,
            "hours": hours,
            "status": status
        })

    path = f"{REPORT_DIR}daily_summary_{date_str}.csv"
    save_csv(path, fieldnames, rows)
    print(f"Daily attendance summary exported: {path}")
    return path


def export_payslips_and_summary():
    """
    HR-only: Generate per-employee payslip PDFs (or .txt fallback) and a payroll summary PDF/txt.
    Uses payroll_inputs.json to get allowance/deduction for each employee for the month.
    """
    if not verify_hr_access():
        return
    month = input("Enter Month-Year (MM-YYYY): ").strip()
    if len(month) != 7 or month[2] != '-':
        print("Invalid format. Use MM-YYYY.")
        return

    employees = load_data(EMPLOYEE_FILE)
    attendance = load_data(ATTENDANCE_FILE)
    payroll_inputs = _load_payroll_inputs()

    summary_lines = [f"PAYROLL SUMMARY - {month}", ""]
    totals = {"reg": 0.0, "ot": 0.0, "gross": 0.0, "net": 0.0}

    for emp in employees:
        emp_id = emp["emp_id"]
        rate = float(emp.get("rate", 0))
        reg_hours = 0.0
        ot_hours = 0.0
        has_att = False

        for entry in attendance:
            if entry.get("emp_id") != emp_id:
                continue
            d = entry.get("date", "")
            if len(d) == 10 and d[:2] == month[:2] and d[6:] == month[3:]:
                has_att = True
                hours = float(entry.get("hours", 0) or 0)
                if hours > REGULAR_HOURS_PER_DAY:
                    reg_hours += REGULAR_HOURS_PER_DAY
                    ot_hours += (hours - REGULAR_HOURS_PER_DAY)
                else:
                    reg_hours += hours

        if not has_att:
            continue

        p_input = next((p for p in payroll_inputs if p.get("emp_id") == emp_id and p.get("month") == month), {})
        allowance = float(p_input.get("allowance", 0))
        deduction = float(p_input.get("deduction", 0))

        gross = (reg_hours * rate) + (ot_hours * rate * OVERTIME_MULTIPLIER) + allowance
        net = gross - deduction

        # create payslip lines
        payslip_lines = []
        payslip_lines.append(f"Payslip for {emp.get('name')} (ID: {emp_id})")
        payslip_lines.append(f"Department: {emp.get('dept')} | Role: {emp.get('role')}")
        payslip_lines.append(f"Period: {month}")
        payslip_lines.append("-" * 48)
        payslip_lines.append(f"Rate/hr: ₱{rate:.2f}")
        payslip_lines.append(f"Regular Hours: {reg_hours:.2f} hrs")
        payslip_lines.append(f"Overtime Hours: {ot_hours:.2f} hrs")
        payslip_lines.append(f"Regular Pay: ₱{reg_hours * rate:.2f}")
        payslip_lines.append(f"Overtime Pay: ₱{ot_hours * rate * OVERTIME_MULTIPLIER:.2f}")
        payslip_lines.append(f"Allowances: ₱{allowance:.2f}")
        payslip_lines.append(f"Deductions: ₱{deduction:.2f}")
        payslip_lines.append("-" * 48)
        payslip_lines.append(f"GROSS PAY: ₱{gross:.2f}")
        payslip_lines.append(f"NET PAY: ₱{net:.2f}")

        payslip_path = f"{REPORT_DIR}payslip_emp_{emp_id}_{month}.pdf"
        # if reportlab not installed, save_pdf will fallback to txt
        save_pdf(payslip_path, f"Payslip - {emp.get('name')} - {month}", payslip_lines)

        # append to summary
        summary_lines.append(f"{emp.get('name')} (ID: {emp_id}): Reg {reg_hours:.2f} | OT {ot_hours:.2f} | Gross ₱{gross:.2f} | Net ₱{net:.2f}")

        totals["reg"] += reg_hours
        totals["ot"] += ot_hours
        totals["gross"] += gross
        totals["net"] += net

    # add totals to summary lines
    summary_lines.append("")
    summary_lines.append("=" * 48)
    summary_lines.append(f"TOTAL Regular Hours: {totals['reg']:.2f}")
    summary_lines.append(f"TOTAL Overtime Hours: {totals['ot']:.2f}")
    summary_lines.append(f"TOTAL GROSS: ₱{totals['gross']:.2f}")
    summary_lines.append(f"TOTAL NET: ₱{totals['net']:.2f}")

    summary_path = f"{REPORT_DIR}payroll_summary_{month}.pdf"
    save_pdf(summary_path, f"Payroll Summary - {month}", summary_lines)

    print(f"Payslips and payroll summary exported to {REPORT_DIR}")
    return REPORT_DIR

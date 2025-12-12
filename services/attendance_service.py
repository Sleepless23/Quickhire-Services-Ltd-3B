from datetime import datetime
from utils.data_handler import load_data, save_data
from utils.security import verify_hr_access
from config import ATTENDANCE_FILE, DATE_FORMAT, DATETIME_FORMAT, HR_PASSWORD


def sign_in():
    """Sign in an employee"""
    attendance = load_data(ATTENDANCE_FILE)
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    today = datetime.now().strftime(DATE_FORMAT)
    
    # Check if already signed in
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == today and not entry.get("sign_out"):
            print("Already signed in today!")
            return
    
    sign_in_time = datetime.now().strftime(DATETIME_FORMAT)
    new_entry = {
        "emp_id": emp_id,
        "date": today,
        "sign_in": sign_in_time,
        "sign_out": None,
        "hours": 0.0
    }
    
    attendance.append(new_entry)
    save_data(ATTENDANCE_FILE, attendance)
    print("Signed in successfully!")


def sign_out():
    """Sign out an employee"""
    attendance = load_data(ATTENDANCE_FILE)
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    today = datetime.now().strftime(DATE_FORMAT)
    
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == today and not entry.get("sign_out"):
            sign_out_time = datetime.now().strftime(DATETIME_FORMAT)
            entry["sign_out"] = sign_out_time
            
            # Calculate hours
            in_time = datetime.strptime(entry["sign_in"], DATETIME_FORMAT)
            out_time = datetime.strptime(sign_out_time, DATETIME_FORMAT)
            hours = (out_time - in_time).total_seconds() / 3600
            entry["hours"] = round(hours, 2)
            
            save_data(ATTENDANCE_FILE, attendance)
            print(f"Signed out! Hours today: {entry['hours']}")
            return
    
    print("No sign-in found for today!")


def edit_attendance():
    
    if not verify_hr_access():
        return
    """Edit attendance records (HR only)"""
    password = input("Enter HR Password: ")
    if password != HR_PASSWORD:
        print("Access denied! For HR only!")
        return
    
    attendance = load_data(ATTENDANCE_FILE)
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid Employee ID!")
        return
    
    date = input("Date [MM-DD-YYYY]: ")
    
    for entry in attendance:
        if entry["emp_id"] == emp_id and entry["date"] == date:
            print(f"\nCurrent: In {entry['sign_in']}, Out {entry['sign_out']}, Hours {entry['hours']}")
            
            new_signin = input("New Sign-In [MM-DD-YYYY HH:MM:SS] or press Enter to skip: ")
            if new_signin:
                try:
                    datetime.strptime(new_signin, DATETIME_FORMAT)
                    entry["sign_in"] = new_signin
                except ValueError:
                    print("Invalid format! Keeping old sign-in time.")
            
            new_signout = input("New Sign-Out [MM-DD-YYYY HH:MM:SS] or press Enter to skip: ")
            if new_signout:
                try:
                    datetime.strptime(new_signout, DATETIME_FORMAT)
                    entry["sign_out"] = new_signout
                except ValueError:
                    print("Invalid format! Keeping old sign-out time.")
            
            # Recalculate hours if both times are present
            if entry["sign_in"] and entry["sign_out"]:
                try:
                    in_time = datetime.strptime(entry["sign_in"], DATETIME_FORMAT)
                    out_time = datetime.strptime(entry["sign_out"], DATETIME_FORMAT)
                    
                    if out_time > in_time:
                        hours = (out_time - in_time).total_seconds() / 3600
                        entry["hours"] = round(hours, 2)
                        print(f"Updated hours: {entry['hours']}")
                    else:
                        print("Warning: Out time must be after in time.")
                except ValueError:
                    print("Invalid time format!")
            
            save_data(ATTENDANCE_FILE, attendance)
            print("Attendance updated successfully!")
            return
    
    print("Entry not found.")
import json

def load_data(filename):
    """Load data from JSON file"""
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(filename, data):
    """Save data to JSON file"""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def get_next_employee_id(employees):
    """Get the next available employee ID"""
    if not employees:
        return 1
    
    highest_id = max(emp["emp_id"] for emp in employees)
    return highest_id + 1
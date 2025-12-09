from config import HR_PASSWORD
from getpass import getpass

def verify_hr_access():
   
    password = getpass("Enter HR Password: ")
    if password != HR_PASSWORD:
        print("Access denied! For HR only!")
        return False
    return True
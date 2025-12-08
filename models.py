class Employee:
    """Employee class to represent employee data"""
    
    def __init__(self, emp_id, name, role, dept, rate, contact):
        self.emp_id = emp_id
        self.name = name
        self.role = role
        self.dept = dept
        self.rate = rate
        self.contact = contact
    
    def to_dict(self):
        """Convert employee object to dictionary"""
        return {
            "emp_id": self.emp_id,
            "name": self.name,
            "role": self.role,
            "dept": self.dept,
            "rate": self.rate,
            "contact": self.contact
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create employee object from dictionary"""
        return cls(
            data["emp_id"],
            data["name"],
            data["role"],
            data["dept"],
            data["rate"],
            data["contact"]
        )
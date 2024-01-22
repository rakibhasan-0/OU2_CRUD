class Library_User:
    def __init__(self, name, email, phone_number, address, ssn, fine_amount):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.ssn = ssn
        self.fine_amount = fine_amount

    def __str__(self):
        return f"LibraryUser(Name: {self.name}, Email: {self.email}, Phone: {self.phone_number}, Address: {self.address}, SSN: {self.ssn}, Fine Amount: {self.fine_amount})"

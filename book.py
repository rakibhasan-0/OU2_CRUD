class Library_Book:
    def __init__(self, title, author, genre, available, book_id):
        self.book_id = book_id
        self.name = title
        self.author = author
        self.genre = genre
        self.available = available

    def __str__(self):
        return f"Library_Book( Id: {self.book_id},  Name: {self.name}, Author: {self.author}, Genre: {self.genre}, Available: {self.available})"

    
        
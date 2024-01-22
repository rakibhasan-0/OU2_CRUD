class Library_Book:
    def __init__(self, name, author, genre, available):
        self.name = name
        self.author = author
        self.genre = genre
        self.available = available

    def __str__(self):
        return f"Library_Book(Name: {self.name}, Author: {self.author}, Genre: {self.genre}, Available: {self.available})"

    
        
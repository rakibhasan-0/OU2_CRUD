from flask import Flask, render_template, redirect, url_for
from Library_user import Library_User
from Library_book import Library_Book
import psycopg2
import os

# The library User has fine cols thus update ER diagram.
# The fine cols has fine amount col

app = Flask(__name__)

# Database connection's configuration
db_config = {
    "host": "localhost",
    "database": "library",
    "user": "postgres",
    "password": "123456",
}


def create_tables():
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    create_book_table(cursor, connection)
    create_user_table(cursor, connection)
    create_loan_table(cursor, connection)
    create_fine_table(cursor, connection)
    cursor.close()
    connection.close()



def create_book_table(cursor, connection):
    book_table = """
    CREATE TABLE IF NOT EXISTS Book (
        book_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        book_name VARCHAR(255) NOT NULL,
        book_genre VARCHAR(255) NOT NULL,
        book_author VARCHAR(255) NOT NULL,
        book_available BOOLEAN NOT NULL DEFAULT TRUE
    );"""
    cursor.execute(book_table)
    connection.commit()



def create_user_table(cursor, connection):
    user_table = """
        CREATE TABLE IF NOT EXISTS Library_User(
            usr_ssn INT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            user_email VARCHAR(255) NOT NULL,
            user_phone_number VARCHAR(255),
            user_address VARCHAR(255), 
            total_fines INT DEFAULT 0 
        );
    """
    #some users cols have deleted.

    cursor.execute(user_table)
    connection.commit()





def create_fine_table(cursor, connection):
    fine_table = """
        CREATE TABLE IF NOT EXISTS Fine(
            fine_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            loan_id INT NOT NULL,
            fine_amount INT NOT NULL DEFAULT 10,
            FOREIGN KEY (loan_id) REFERENCES Loan(loan_id)
        );
    """
    cursor.execute(fine_table)
    connection.commit()



def create_loan_table(cursor, connection):
    loan_table = """
        CREATE TABLE IF NOT EXISTS Loan(
            loan_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            book_id INT NOT NULL,
            usr_ssn INT NOT NULL,
            loan_date DATE NOT NULL,
            return_date DATE,
            FOREIGN KEY (book_id) REFERENCES Book(book_id),
            FOREIGN KEY (usr_ssn) REFERENCES Library_User(usr_ssn)
        );
    """
    cursor.execute(loan_table)
    connection.commit()




@app.route("/")
def index():
    user = Library_User("John Doe", "kS9f9@example.com", "1234567890", "123 Main Street", 123456789, 0)
    book_id = 3213
    return render_template('input.html')


if __name__ == "__main__":
    create_tables()
    print("there")
    app.run(debug=True)


















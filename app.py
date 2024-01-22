from flask import Flask, render_template, redirect, url_for
from Library_user import LibraryUser
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
    user = LibraryUser("John Doe", "johndoe@example.com", 9710232, "123 Main St", 123414, 0)
    print(user)  # This should print the user's details in the console
    return render_template("user_update.html", library_user=user)



if __name__ == "__main__":
    create_tables()
    print("there")
    app.run(debug=True)


















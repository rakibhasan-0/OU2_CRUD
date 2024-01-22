import logging
from flask import Flask, render_template, redirect, url_for,request
from library_user import Library_User
from book import Library_Book
from db_connection import create_tables, get_db_connection, close_db_connection
import os

# The library User has fine cols thus update ER diagram.
# The fine cols has fine amount col

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('input.html')

@app.route("/insert_user_info", methods=["POST", "GET"])
def insert_user_info():
    try:
        user_name = request.form.get("user_name")
        user_email = request.form.get("user_email")
        user_phone_number = request.form.get("user_phone_number")
        user_address = request.form.get("user_address")
        user_ssn = request.form.get("user_ssn")
    

        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO Library_User (usr_ssn, user_name, user_email, user_phone_number, user_address)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_ssn, user_name, user_email, user_phone_number, user_address))
        connection.commit()

    except Exception as e:
        logging.error("An error occurred: %s", e)

    finally:
        close_db_connection(connection)
        return render_template('input.html')



@app.route("/insert_book_info", methods=["POST", "GET"])
def insert_book_info():
    try:
        book_name = request.form.get("book_name")
        book_genre = request.form.get("book_genre")
        book_author = request.form.get("book_author")
        
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO Book (book_name, book_genre, book_author)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (book_name, book_genre, book_author))
        connection.commit()

    except Exception as e:
        logging.error("An error occurred: %s", e)

    finally:
        close_db_connection(connection)
        return render_template('input.html')





@app.route('/available_books')
def available_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Book WHERE book_available = true")
    books_data = cursor.fetchall()   
    cursor.close()
    close_db_connection(connection)
    book_objects = [Library_Book(title=book[1], author=book[3], genre=book[2], available=book[4], book_id=book[0]) for book in books_data]

    return render_template('available_books.html', active_page='available_books', books=book_objects)

    

@app.route('/')
def home():
    return render_template('input.html', active_page='home')



if __name__ == "__main__":
    create_tables()
    app.run(debug=True)

















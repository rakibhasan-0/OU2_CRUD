from app import app
import datetime 
from datetime import date, timedelta
import logging
from flask import Flask, render_template, redirect, url_for,request
from library_user import Library_User
from book import Library_Book
from db_connection import create_tables, get_db_connection, close_db_connection
import os





#view
@app.route('/')
def home():
    return render_template('input.html', active_page='home')


#view
@app.route("/users_list")
def users_list():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Library_User")
        users = cursor.fetchall()
        users_objects = [Library_User(name=user[1], email=user[2], phone_number=user[3], address=user[4], ssn=user[0], fine_amount=user[5]) for user in users]

    finally:
        close_db_connection(connection)
        return render_template('users_list.html',active_page ='users_list', users=users_objects)
    





#view
@app.route('/available_books', methods = ["POST", "GET"])
def available_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Book WHERE book_available = true")
    books_data = cursor.fetchall()   
    cursor.close()
    close_db_connection(connection)
    book_objects = [Library_Book(title=book[1], author=book[3], genre=book[2], available=book[4], book_id=book[0]) for book in books_data]

    return render_template('available_books.html', active_page='available_books', books=book_objects)





#view
@app.route('/book_info', methods=["POST", "GET"])
def get_book_info():
    library_book = None

    if request.method == "POST":
        connection = get_db_connection()
        cursor = connection.cursor()
        book_id = request.form.get("book_update_id")
        print("The book id is: " + book_id)

        if book_id:
            cursor.execute("SELECT * FROM Book WHERE book_id = %s", (book_id,))
            book_data = cursor.fetchone()
            close_db_connection(connection)

            if book_data:
                library_book = Library_Book(title=book_data[1], author=book_data[3], genre=book_data[2], available=book_data[4], book_id=book_data[0])
                return render_template('book_update.html', library_book=library_book)
            else:
                print("No book found with ID:", book_id)
       
    return render_template('input.html')
    




#view
@app.route('/get_user_info', methods = ["POST", "GET"])
def get_user_info():
    connection = get_db_connection()
    cursor = connection.cursor()
    user_ssn = request.form.get("user_info_person_num")
    cursor.execute("SELECT * FROM Library_User WHERE usr_ssn = %s", (user_ssn,))
    users = cursor.fetchone()
    users = Library_User(name=users[1], email=users[2], phone_number=users[3], address=users[4], ssn=users[0], fine_amount=users[5])
    return render_template('user_update.html', library_user=users)




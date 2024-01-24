from app import app
import datetime 
from datetime import date, timedelta
import logging
from flask import Flask, render_template, redirect, url_for,request
from library_user import Library_User
from book import Library_Book
from db_connection import create_tables, get_db_connection, close_db_connection
import os


# it used for create user info
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
    




#model, it used for creating book info
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
    




#model, it used for creating loan info
# trigger will be added here in order to update the book's availability.
@app.route('/make_loan', methods=["POST", "GET"])
def make_loan():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            user_ssn = request.form.get("user_person_num")
            book_id = request.form.get("make_loan_book_id")
            loan_date = request.form.get("loan_date")

            date_format = "%Y-%m-%d"
            loan_date = datetime.datetime.strptime(loan_date, date_format)

            # Check if the book is available
            cursor.execute("SELECT book_available FROM Book WHERE book_id = %s", (book_id,))
            book_record = cursor.fetchone()
            if book_record is None or not book_record[0]:
                raise ValueError("Book is not available or does not exist")

            # Check if the user exists
            cursor.execute("SELECT usr_ssn FROM Library_User WHERE usr_ssn = %s", (user_ssn,))
            if cursor.fetchone() is None:
                raise ValueError("User does not exist")

            # Insert the new loan
            insert_query = "INSERT INTO Loan (usr_ssn, book_id, loan_date) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (user_ssn, book_id, loan_date))
            conn.commit()

        except ValueError as e:
            logging.error("Validation error: %s", e)

        except Exception as e:
            logging.error("An error occurred: %s", e)

        finally:
            close_db_connection(conn)

    return render_template('input.html')




#model
#it will calc the returned date and update the fine amount and book availability
@app.route('/return_loan', methods=["POST", "GET"])
def return_book():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            user_ssn = request.form.get("loaned_person_num")
            book_id = request.form.get("loaned_book_id")
            return_date = request.form.get("loaned_return_date")

            date_format = "%Y-%m-%d"  
            parsed_datetime = datetime.datetime.strptime(return_date, date_format)
            return_date = parsed_datetime.date()


            # a user can make several make to the same loan
            # thus, we may grab all of the loans, then check the return date of each loan, if any of the loans return date is null then we will process that loan.
            cursor.execute("SELECT loan_id FROM Loan WHERE book_id = %s AND usr_ssn = %s", (book_id, user_ssn))
            loan_ids = cursor.fetchall()

            process_loan_id = None
            loan_to_process = None

            for loan_id_tuple in loan_ids:
                loan_id = loan_id_tuple[0]
                cursor.execute("SELECT loan_date, return_date FROM Loan WHERE loan_id = %s", (loan_id,))
                loan_record = cursor.fetchone()

                if loan_record and loan_record[1] is None: 
                    process_loan_id = loan_id
                    loan_to_process = loan_record
                    break 
            
            
            if loan_to_process:

                delta = return_date - loan_to_process[0]
                loan_id = process_loan_id

                if delta.days > 10:
                    fine_amount = 2 * delta.days
                    cursor.execute("UPDATE Library_User SET total_fines = total_fines + %s WHERE usr_ssn = %s", (fine_amount, user_ssn))
                    cursor.execute("Insert into Fine(loan_id, fine_amount) values(%s, %s)", (loan_id, fine_amount)) 

                # whether the user deserved the fine or not, once the book is returned, we will update the book availability 
                # and the update the return date of the loan                 
                cursor.execute("UPDATE Loan SET return_date = %s WHERE loan_id = %s", (return_date, loan_id))
                cursor.execute("UPDATE Book SET book_available = true WHERE book_id = %s", (book_id,))
                conn.commit()

            else:
                raise ValueError("Book not loaned")       

        except Exception as e:
            logging.error("An error occurred: %s", e)

        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))




#model
@app.route('/delete_user', methods=["POST", "GET"])
def delete_user():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            user_ssn = request.form.get("user_delete")

            cursor.execute("SELECT loan_id FROM Loan WHERE usr_ssn = %s", (user_ssn,))
            loan_ids = cursor.fetchall()

            for loan_id_tuple in loan_ids:
                loan_id = loan_id_tuple[0]
                cursor.execute("DELETE FROM Fine WHERE loan_id = %s", (loan_id,))
                cursor.execute("DELETE FROM Loan WHERE loan_id = %s", (loan_id,))

            cursor.execute("DELETE FROM library_user WHERE usr_ssn = %s", (user_ssn,))

            conn.commit()

        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))
        



#model
@app.route('/delete_book', methods=["POST", "GET"])
def delete_book():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            book_id = request.form.get("book_delete")

            #if book is available in the library then we will delete it        
            cursor.execute("SELECT book_available FROM Book WHERE book_id = %s", (book_id,))
            book_record = cursor.fetchone()
            if book_record:
                cursor.execute("DELETE FROM Book WHERE book_id = %s", (book_id,))
            else:
                raise ValueError("Book is not available or does not exist")

            conn.commit()

        except Exception as e:
            logging.error("An error occurred: %s", e)

        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))





# you need to fix it to get the user info
#model
@app.route('/get_user_info/update_user_info', methods=["POST", "GET"])

def update_user_info():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            user_ssn = request.form.get("user_ssn")
            name = request.form.get("user_name")
            email = request.form.get("user_email")
            phone_number = request.form.get("user_phone")
            address = request.form.get("user_address")

            print(user_ssn, name, email, phone_number, address)

            cursor.execute("UPDATE Library_User SET user_name = %s, user_email = %s, user_phone_number = %s, user_address = %s WHERE usr_ssn = %s", (name, email, phone_number, address, user_ssn))
            conn.commit()


        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))




#model
@app.route('/book_info/update_book_info', methods=["POST", "GET"])
def update_book_info():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            book_id = request.form.get("book_id")
            name = request.form.get("book_name")
            genre = request.form.get("book_genre")
            author = request.form.get("book_author")

            print(book_id, name, genre, author)

            cursor.execute("UPDATE Book SET book_name = %s, book_genre = %s, book_author = %s WHERE book_id = %s", (name, genre, author, book_id))
            conn.commit()


        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))














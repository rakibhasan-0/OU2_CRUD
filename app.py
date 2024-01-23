import datetime 
from datetime import date, timedelta
import logging
from flask import Flask, render_template, redirect, url_for,request
from library_user import Library_User
from book import Library_Book
from db_connection import create_tables, get_db_connection, close_db_connection
import os

# The library User has fine cols thus update ER diagram.
# The fine cols has fine amount col

app = Flask(__name__)

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




@app.route('/update_book_info', methods=["POST", "GET"])
def update_book_info():
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
                library_book = Library_Book(title=book_data[1], author=book_data[2], genre=book_data[3], available=book_data[4], book_id=book_data[0])
            else:
                print("No book found with ID:", book_id)
                # Handle the case where no book is found

    return render_template('book_update.html', library_book=library_book)



@app.route('/get_user_info', methods = ["POST", "GET"])
def get_user_info():
    connection = get_db_connection()
    cursor = connection.cursor()
    user_ssn = request.form.get("user_info_person_num")
    cursor.execute("SELECT * FROM Library_User WHERE usr_ssn = %s", (user_ssn,))
    users = cursor.fetchone()
    users = Library_User(name=users[1], email=users[2], phone_number=users[3], address=users[4], ssn=users[0], fine_amount=users[5])
    return render_template('user_update.html', library_user=users)






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
                print(return_date)
                print(type(return_date))
                print(type(loan_to_process))
                print(loan_to_process)
                print(delta)
                if delta.days > 10:
                    fine_amount = 2 * delta.days
                    print(fine_amount)
                    cursor.execute("UPDATE Library_User SET total_fines = total_fines + %s WHERE usr_ssn = %s", (fine_amount, user_ssn))
                    loan_id = process_loan_id

                    print(loan_id)

                    cursor.execute("UPDATE Loan SET return_date = %s WHERE loan_id = %s", (return_date, loan_id))
                    cursor.execute("Insert into Fine(loan_id, fine_amount) values(%s, %s)", (loan_id, fine_amount))   

                cursor.execute("UPDATE Book SET book_available = true WHERE book_id = %s", (book_id,))
                conn.commit()
            else:
                raise ValueError("Book not loaned")       

        except Exception as e:
            logging.error("An error occurred: %s", e)

        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))





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
        


@app.route('/delete_book', methods=["POST", "GET"])
def delete_book():
    print("hello")
    if request.method == "POST":
        try:
            print("hello")
            conn = get_db_connection()
            cursor = conn.cursor()
            book_id = request.form.get("book_delete")

            #if book is available in the library then we will delete it
        
            cursor.execute("SELECT book_available FROM Book WHERE book_id = %s", (book_id,))
            book_record = cursor.fetchone()
            if book_record:
                print("bokk deletion")
                cursor.execute("DELETE FROM Book WHERE book_id = %s", (book_id,))
            else:
                raise ValueError("Book is not available or does not exist")

            conn.commit()

        except Exception as e:
            logging.error("An error occurred: %s", e)

        finally:
            close_db_connection(conn)
            return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('input.html', active_page='home')



if __name__ == "__main__":
    create_tables()
    app.run(debug=True)

















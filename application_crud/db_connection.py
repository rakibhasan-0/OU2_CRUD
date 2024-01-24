import psycopg2
# Database connection's configuration
db_config = {
    "host": "localhost",
    "database": "library",
    "user": "postgres",
    "password": "123456",
}

def get_db_connection():
    connection = psycopg2.connect(**db_config)
    return connection


def close_db_connection(connection):
    connection.close()


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    create_book_table(cursor, connection)
    create_user_table(cursor, connection)
    create_loan_table(cursor, connection)
    create_fine_table(cursor, connection)
    create_book_unavailable_trigger_function(cursor, connection)
    create_book_unavailable_trigger(cursor, connection)

    cursor.close()
    close_db_connection(connection)



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


def create_book_unavailable_trigger_function(cursor, connection):
    trigger_function = """
    CREATE OR REPLACE FUNCTION set_book_unavailable()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE Book
        SET book_available = FALSE
        WHERE book_id = NEW.book_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """

    cursor.execute(trigger_function)
    connection.commit()



def create_book_unavailable_trigger(cursor, connection):
  
    drop_trigger = """
    DROP TRIGGER IF EXISTS book_unavailable_trigger ON Loan;
    """
    cursor.execute(drop_trigger)

    create_trigger = """
    CREATE TRIGGER book_unavailable_trigger
    AFTER INSERT ON Loan
    FOR EACH ROW
    EXECUTE FUNCTION set_book_unavailable();
    """
    cursor.execute(create_trigger)
    connection.commit()











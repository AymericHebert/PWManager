import mysql.connector
from rich.console import Console
from rich import print as printc




config = {
    'user' : 'pwm',
    'password' : 'CqWyByt5wuPNPQZ',
    'host' : 'localhost',
    'raise_on_warnings' : True
}


console = Console()


def insert_entry(application_name: str, url: str = None, email: str = None, username: str = None, password: str = None) -> int:
    ''' Insert a password into the database and return it's id '''

    sql = """
        INSERT INTO pwm.entries (application_name, url, email, username, password, created_at, update_at)
        VALUES(%s, %s, %s, %s, %s, DEFAULT, DEFAULT);
    """

    db, password_id  = None, None
    try:
        db = connect()
        cursor = db.cursor()
        cursor.execute(sql, (application_name, url, email, username, password))
        password_id = cursor.lastrowid
        db.commit()
        cursor.close()
    except (Exception, mysql.connector.DatabaseError):
        console.print_exception()
    finally:
        if db is not None:
            db.close()
        return password_id


def retrieve_entries(application_name: str = '', url: str = '', email: str = '', username: str = '') -> list:

    ''' Retrieve all entries from the database that match the given parameters. '''

    sql = """
        SELECT password_id, application_name, url, email, username, created_at, update_at 
        FROM pwm.entries
        WHERE application_name LIKE '%{}%'
        AND url LIKE '%{}%'
        AND email LIKE '%{}%'
        AND username LIKE '%{}%'
    """.format(application_name, url, email, username)

    db, rows = None, None
    try:
        db = connect()
        cursor = db.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
    except (Exception, mysql.connector.DatabaseError):
        console.print_exception()
    finally:
        if db is not None:
            db.close()
        return rows


def get_column_names(return_num_columns: bool = False) -> list:
    ''' Return the column names of the db, can also return the number of columns. '''

    num_columns, columns_names = None, None
    try:
        db = connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pwm.entries")
        num_columns = len(cursor.description)
        columns_names = [i[0] for i in cursor.description]
    except (Exception, mysql.connector.DatabaseError):
        console.print_exception()
    finally:
        if db is not None:
            db.close()
        if return_num_columns: return columns_names, num_columns
        else: return columns_names


def get_num_entries() -> int:
    ''' Return the number of rows in the database. '''

    num_entries = None
    try:
        db = connect()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pwm.entries")
        num_entries = cursor.fetchone()[0]
    except (Exception, mysql.connector.DatabaseError):
        console.print_exception()
    finally:
        if db is not None:
            db.close()
        return num_entries


def connect() -> mysql.connector.connection.MySQLConnection:
    ''' Connect to MySQL Instance. '''

    try:
        db = mysql.connector.connect(**config)
    except (Exception, mysql.connector.Error) as error:
        console.print_exception()
        printc('[red][!] Be sure that the instance you are connecting to is running and that the user and password are correctly set in the dbconnect.py file.')
    finally:
        return db
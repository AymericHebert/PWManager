import psycopg2, os
from configparser import ConfigParser




def delete_password(password_id: int) -> None:
    '''
    Delete one password from the table.
    
    Parameters
    ----------
    password_id : int
    Key of the password to delete.

    '''
    sql = """
        DELETE FROM passwords 
        WHERE password_id = """ + str(password_id) + """;
    """
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = connect()
        cur = conn.cursor()
        # execute the SELECT statement
        cur.execute(sql)
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def search_with_url(url: str) -> dict:
    '''
    Query all passwords from the table that match the url.

    Parameters
    ----------
    url : str
    Url to search for in the database.

    Returns
    -------
    rows: dict
    Rows that corresponds to the sql statement.

    '''
    sql = """
        SELECT * from passwords
        WHERE url
        ILIKE '%""" + str(url) + """%'"""      
    return get_rows(sql)


def search_with_username(username: str) -> dict:
    '''
    Query all passwords from the table that match the username.

    Parameters
    ----------
    username : str
    Username to search for in the database.

    Returns
    -------
    rows: dict
    Rows that corresponds to the sql statement.

    '''
    sql = """
        SELECT * from passwords
        WHERE username 
        ILIKE '%""" + str(username) + """%'"""      
    return get_rows(sql)


def search_all_passwords() -> dict:
    '''
    Query all passwords from the table.
    
    Returns
    -------
    rows: dict
    Rows that corresponds to the sql statement.

    '''
    sql = '''
        SELECT * from passwords
        ORDER BY update_at DESC;
    '''
    return get_rows(sql)


def get_row(password_id: int) -> dict:
    '''
    Query one password from the table.
    
    Parameters
    ----------
    password_id : int
    Key of the password to query.

    Returns
    -------
    rows: dict
    Rows that corresponds to the sql statement.

    '''
    sql = """
        SELECT * from passwords
        WHERE password_id = """ + str(password_id) + """;
    """
    return get_rows(sql)


def get_rows(sql: str) -> dict:
    '''
    Return rows of the database for sql statement.

    Parameters
    ----------
    sql : str
    SQL statement to query the database.

    Returns
    -------
    rows: dict
    Rows that corresponds to the sql statement.
    
    '''

    conn = None
    fetched = None
    rows = {}
    try:
        # connect to the PostgreSQL server
        conn = connect()
        cur = conn.cursor()
        # execute the SELECT statement
        cur.execute(sql)
        # fetch the rows
        fetched = cur.fetchall()
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None and fetched is not None:
            conn.close()

            for i in range(len(fetched)):
                rows[i] = {}
                rows[i]['password_id'] = str(fetched[i][0])
                rows[i]['application_name'] = str(fetched[i][1])
                rows[i]['url'] = str(fetched[i][2])
                rows[i]['username'] = str(fetched[i][3])
                rows[i]['password'] = str(fetched[i][4])
                rows[i]['created_at'] = str(fetched[i][5])
                rows[i]['update_at'] = str(fetched[i][6])

            return rows


def update_password(password_id: int, application_name: str, url: str, username: str, password: str) -> None:
    '''
    Update a password in the table.

    Parameters
    ----------
    password_id : int
    Key of the password to update.
    application_name: str
    The name of the table application / website.
    url: str
    Url of the application / website.
    username: str
    Username / email for the login. 
    password: str
    Password for the login.
            
    Returns
    -------
    password_id: id
    Id of the newly created password.

    '''

    '''
    WILL SEE IF I NEED THIS
    '''
    # row = get_row(password_id)

    # if application_name is None:
    #     application_name = row[0]['application_name']

    # if url is None:
    #     url = row[0]['url']
    
    # if username is None:
    #     username = row[0]['username']

    # if password is None:
    #     password = row[0]['password']

    sql = '''
        UPDATE passwords
        SET application_name = %s,
        url = %s,
        username = %s, 
        password = %s,
        update_at = DEFAULT
        WHERE password_id = %s;
    '''
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = connect()
        cur = conn.cursor()
        # execute the UPDATE  statement
        cur.execute(sql, (application_name, url, username, password, password_id,))
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_password(application_name: str, url=None, username=None, password=None) -> int:
    '''
    Insert new password in the table.

    Parameters
    ----------
    application_name: str
    The name of the table application / website.
    url: str
    Url of the application / website.
    username: str
    Username / email for the login. 
    password: str
    Password for the login.
            
    Returns
    -------
    password_id: id
    Id of the newly created password.
    
    '''
    sql = '''
        INSERT INTO passwords(application_name, url, username, password, created_at, update_at) 
        VALUES(%s, %s, %s, %s, DEFAULT, DEFAULT)
        RETURNING password_id;
    '''
    conn = None
    password_id = None
    try:
        # connect to the PostgreSQL server
        conn = connect()
        cur = conn.cursor()
        # insert the new password in the table
        cur.execute(sql, (application_name, url, username, password,))
        # get the generated id back
        password_id = cur.fetchone()[0]
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return password_id


def create_password_table() -> None:
    """ 
    Create a password table in the PostgreSQL database.   
    
    """

    command = (
        """
        CREATE TABLE passwords (
            password_id SERIAL PRIMARY KEY,
            application_name VARCHAR(255) NOT NULL,
            url VARCHAR(255),
            username VARCHAR(100),
            password VARCHAR(100),
            created_at TIMESTAMPTZ DEFAULT Now()::timestamptz,
            update_at TIMESTAMPTZ DEFAULT Now()::timestamptz
        );
        """
    )

    if table_exists('passwords'):
        return

    conn = None
    try:
        # connect to the PostgreSQL server
        conn = connect()
        cur = conn.cursor()
        # create the table
        cur.execute(command)
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()


def table_exists(table_name: str) -> bool:
    '''
    Check if the table already exists within the database.

    Parameters
    ----------
    table_name : str
    The name of the table created.    
            
    Returns
    -------
    exists : bool
    True if the table exists within the database.
    
    '''
    exists = False
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("select exists(select relname from pg_class where relname='" + table_name + "')")
        exists = cur.fetchone()[0]
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(error)
    return exists

    
def connect() -> psycopg2.extensions.connection:
    '''
    Return the connection to a PostgreSQL server.
            
    Returns
    -------
    conn: psycopg2.extensions.connection
    connection to the server
    
    '''
    try:
        filepath = os.path.join(os.path.dirname(__file__),"config.ini")
        params = _get_params(filename=filepath, section='postgresql')
        conn = psycopg2.connect(**params)
        return conn

    except (Exception, psycopg2.Error) as error:
        print(error)


def _get_params(filename: str, section: str) -> dict:
    '''
    Get all the parameters from a section of the config file.

    Parameters
    ----------
    filename : str
    Name of the file.
    section : str
    Name of the section containing the parameters.
            
    Returns
    -------
    db : dict
    A dictionary containing the parameters
    
    '''
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
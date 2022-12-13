import os
import time

import mysql.connector
from dotenv import load_dotenv




dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv('.env')

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')

config = {
     'user': USER,
     'password': PASSWORD,
     'host': HOST,
     'raise_on_warnings' : True
}

class DBManager(object):

    def __init__(self, db_name:str, config: dict) -> None:
        self.db_name = db_name
        self.config = config
        self.__get_tables()


    def __connect(self) -> mysql.connector.connection.MySQLConnection:
        ''' Connect to MySQL Instance. '''

        try:
            conn = mysql.connector.connect(**self.config)
        except (Exception, mysql.connector.Error) as error:
            print(error)
        finally:
            return conn


    def db_exists(self) -> bool:
        ''' Check if the database already exists. '''
        
        query = """
        SELECT SCHEMA_NAME 
        FROM INFORMATION_SCHEMA.SCHEMATA  
        WHERE SCHEMA_NAME = %s
        """

        exists = False
        conn = None
        try:
            conn = self.__connect()
            cursor = conn.cursor()
            cursor.execute(query, (self.db_name,))
            results = cursor.fetchall()
            cursor.close()
        except (Exception, mysql.connector.Error) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            if len(results)!=0: exists = True
            return exists


    def create_db(self) -> None:
        ''' Create the database if it doesn't exists. '''

        if self.db_exists():
            return

        conn = None
        try:
            conn = self.__connect()
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE %s"%self.db_name)
            cursor.close()
        except (Exception, mysql.connector.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()


    def __get_tables(self) -> list:
        ''' Update tables in the database. '''

        if not self.db_exists():
            return None

        conn = None
        tables = None
        try:
            conn = self.__connect()
            cursor = conn.cursor()
            cursor.execute("USE %s"%self.db_name)
            cursor.execute("SHOW TABLES")
            res = cursor.fetchall()
            if len(res) > 0: tables = res[0]
            cursor.close()
        except (Exception, mysql.connector.Error) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            self.tables = tables


    def table_exists(self, table_name: str) -> bool:
        ''' Check if table exists in the database. '''

        self.__get_tables()
        return table_name in self.tables


    def create_table(self, table_name: str, columns: list) -> None:
        ''' Add table to the database. '''
        sql = """CREATE TABLE {}.{} ({})""".format(self.db_name, table_name, columns)

        conn = None
        try:
            conn = self.__connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        except (Exception, mysql.connector.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            self.__get_tables()


    def delete_db(self) -> None:
        ''' Delete the database if it exists. '''

        if not self.db_exists():
            return

        try:
            conn = self.__connect()
            cursor = conn.cursor()
            cursor.execute("DROP DATABASE %s"%self.db_name)
            conn.commit()
            cursor.close()
        except (Exception, mysql.connector.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            self.__get_tables()


    def delete_table(self, table_name: str) -> None:
        ''' Delete the table if it exists. '''

        if not self.table_exists(table_name):
            return

        try:
            conn = self.__connect()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE %s"%table_name)
            conn.commit()
            cursor.close()
        except (Exception, mysql.connector.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            self.__get_tables()
        

start = time.time()
db = DBManager(db_name="pwm", config=config)
print(db.tables)
end = time.time()
print ('Total time: ' + time.strftime("%H:%M:%S", time.gmtime(end - start)))

import time

import mysql.connector

from configloader import get_config




class DBManager(object):

    def __init__(self, db_name:str, config: dict) -> None:
        self.db_name = db_name
        self.config = config
        self.get_tables()


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


    def get_tables(self) -> list:
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

        self.get_tables()
        return table_name in self.tables


    def create_table(self, table_name: str, columns: list) -> None:
        ''' Add table to the database. '''

        # make column string for sql statement
        columns_str = ''
        for column in columns:
            columns_str = "".join([columns_str, column + ', '])
        columns_str = columns_str[:-2]

        sql = """CREATE TABLE {}.{} ({})""".format(self.db_name, table_name, columns_str)

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
            self.get_tables()


    def delete_db(self) -> None:
        ''' Delete the database if it exists. '''

        if not self.db_exists():
            return

        conn = None
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
            self.get_tables()


    def delete_table(self, table_name: str) -> None:
        ''' Delete the table if it exists. '''

        if not self.table_exists(table_name):
            return

        conn = None
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
            self.get_tables()


    def get_column_names(self, table_name: str, return_num_columns: bool = False) -> list:
        ''' Return the column names of the db, can also return the number of columns. '''

        conn = None
        num_columns, columns_names = None, None
        try:
            conn = self.__connect()
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT * FROM %s.%s"%(self.db_name, table_name))
            num_columns = len(cursor.description)
            columns_names = [i[0] for i in cursor.description]
            cursor.close()
        except (Exception, mysql.connector.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            if return_num_columns: return columns_names, num_columns
            else: return columns_names


    def insert(self, table_name: str, columns: list, values: list) -> int:
        ''' Insert an entry into the database. '''
        
        # check if columns and values are the same length
        if len(columns) != len(values): raise Exception("A value must be given for each column.")

        # check if the columns provided exists in the table
        table_columns = self.get_column_names(table_name)
        for column in columns:
            if column not in table_columns: raise Exception("%s column doesn't exist in the table."%column)

        # make column string for sql statement
        columns_str = ', '.join(columns)
        
        # make value string for sql statement
        values_str = ''
        for value in values:
            values_str = "".join([values_str, "'%s'"%value + ', '])
        values_str = values_str[:-2]

        sql = """ INSERT INTO %s.%s (%s) VALUES (%s)"""%(self.db_name, table_name, columns_str, values_str)

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
        

start = time.time()
config = get_config()
db = DBManager(db_name="pwm", config=config)
end = time.time()
print ('Total time: ' + time.strftime("%H:%M:%S", time.gmtime(end - start)))

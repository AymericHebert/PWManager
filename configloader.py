import os
from dotenv import load_dotenv




def get_config():
     ''' Get MySQL config from .env file  '''

     dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
     load_dotenv(dotenv_path)

     USER = os.getenv('USER')
     PASSWORD = os.getenv('PASSWORD')
     HOST = os.getenv('HOST')

     config = {
          'user': USER,
          'password': PASSWORD,
          'host': HOST,
          'raise_on_warnings' : True
     }
     
     return config
import os
from dotenv import load_dotenv
load_dotenv()

DB_DIALECT = os.getenv('DB_DIALECT')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_USER = os.getenv('DB_USER')
headers = os.getenv('headers')
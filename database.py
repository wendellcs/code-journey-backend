import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
load_dotenv()
psycopg2.extras.register_uuid()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
    try:
        yield connection, cursor
        
    finally: 
        cursor.close()
        connection.close()
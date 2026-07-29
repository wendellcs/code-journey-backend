import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        yield connection, cursor
        
    finally: 
        cursor.close()
        connection.close()
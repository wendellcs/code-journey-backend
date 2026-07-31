import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from fastapi import status, HTTPException

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


def count_rows(cursor, table_name: str = 'students') -> int:
    
    allowed_table_names = ['students', 'technologies', 'classes']
    if table_name not in allowed_table_names:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid table.')
    
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    
    return cursor.fetchone()['count']
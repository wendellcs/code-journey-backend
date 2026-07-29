from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psycopg2
import os 

from Schemas.classesSchema import ClassesSchema

app = FastAPI()
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
ORIGIN = os.getenv('ORIGIN')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


def get_connection():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        yield connection, cursor
        
    finally: 
        cursor.close()
        connection.close()


@app.post('/classes/add', status_code = status.HTTP_201_CREATED)
def create_class(class_data: ClassesSchema, db = Depends(get_connection)):
    connection, cursor = db
    
    try:
        cursor.execute('INSERT INTO classes (module, day_of_week, class_time ) VALUES (%s, %s, %s)',
            (class_data.module, class_data.day_of_week, class_data.class_time))
        
        connection.commit()
    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = 'This class is already registered.')
    
    return {'ok': 'Class successfully registered.'}
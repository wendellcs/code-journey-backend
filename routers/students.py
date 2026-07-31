from fastapi import APIRouter, Depends, status, HTTPException
from schemas.studentsSchema import StudentsSchema
import psycopg2
from database import get_connection


router = APIRouter(prefix='/students')

@router.post('/add', status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentsSchema, db = Depends(get_connection)):
    connection , cursor = db 
    
    try:
        cursor.execute('INSERT INTO students (first_name, last_name, age, class_id, tag) VALUES (%s, %s, %s, %s, %s)',
            (student_data.first_name, student_data.last_name, student_data.age, student_data.class_id, student_data.tag))
        connection.commit()
    except psycopg2.errors.CheckViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Age must be greater than 12.')
    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='The chosen tag is already being used.')
    except psycopg2.errors.ForeignKeyViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The referenced class was not found.')
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.classesSchema import ClassesSchema
import psycopg2
from datetime import time
from database import get_connection

router = APIRouter(prefix='/classes')

@router.get('/find', status_code=status.HTTP_200_OK)
def find_class(module:str, day_of_week:str, class_time:time , db = Depends(get_connection)):
    _, cursor = db

    cursor.execute('SELECT id FROM classes WHERE module=%s AND day_of_week=%s AND class_time=%s',
        (module, day_of_week, class_time))
    
    class_id = cursor.fetchone()
    
    if class_id:
        return class_id[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Class not found.')
   

@router.post('/add', status_code = status.HTTP_201_CREATED)
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
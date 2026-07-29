from fastapi import APIRouter, Depends, status, HTTPException
from schemas.classesSchema import ClassesSchema
import psycopg2
from database import get_connection

router = APIRouter(prefix='/classes')

@router.post('/classes/add', status_code = status.HTTP_201_CREATED)
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
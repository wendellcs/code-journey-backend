from fastapi import APIRouter, Depends, status, HTTPException
from schemas.classesSchema import ClassesSchema, EditClassesSchema
import psycopg2
from datetime import time
from database import get_connection, count_rows
import math

router = APIRouter(prefix='/classes')

@router.get('', status_code=status.HTTP_200_OK)
def get_classes(page: int = 1 , limit:int = 4, db = Depends(get_connection)):
    _, cursor = db 
    
    if limit < 2:
        limit = 2
        
    offset = (page - 1) * limit
    
    cursor.execute(f'SELECT * FROM classes ORDER BY created_at LIMIT %s OFFSET %s',
        (limit, offset))
    
    classes = cursor.fetchall()
    total_classes = count_rows(cursor, 'classes')

    return {
        'classes': classes,
        'current_page': page,
        'total_pages': math.ceil(total_classes / limit)
    }
    

@router.get('/all', status_code=status.HTTP_200_OK)
def get_all_classes(db = Depends(get_connection)):
    _, cursor = db 
    
    cursor.execute('SELECT * FROM classes')
    classes = cursor.fetchall()
    
    return classes
    

@router.get('/find', status_code=status.HTTP_200_OK)
def find_class(module:str, day_of_week:str, class_time:time , db = Depends(get_connection)):
    _, cursor = db

    cursor.execute('SELECT id FROM classes WHERE module=%s AND day_of_week=%s AND class_time=%s',
        (module, day_of_week, class_time))
    
    class_id = cursor.fetchone()
    
    if class_id:
        return class_id
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


@router.patch('/edit', status_code=status.HTTP_200_OK)
def edit_class(new_data: EditClassesSchema, db = Depends(get_connection)):
    connection, cursor = db
    clauses = []
    execute_values = []

    if new_data.module:
        clauses.append('module = %s')
        execute_values.append(new_data.module)
    if new_data.day_of_week:
        clauses.append('day_of_week = %s')
        execute_values.append(new_data.day_of_week)
    if new_data.class_time:
        clauses.append('class_time = %s')
        execute_values.append(new_data.class_time)
        
    set_clause = ', '.join(clauses)

    try:
        cursor.execute(f'UPDATE classes SET {set_clause} WHERE id = %s', (*execute_values, new_data.id))
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Class not found')
        
        connection.commit()
    except psycopg2.errors.DataError: 
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid data format')
    

@router.delete('/remove/{class_id}', status_code=status.HTTP_200_OK)
def delete_class(class_id: str, db = Depends(get_connection)):
    connection, cursor = db
    
    cursor.execute('DELETE FROM classes WHERE id = %s', (class_id,))
        
    if cursor.rowcount == 0:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Class not found')
    
    connection.commit()
    
    return {'ok': 'Class successfully deleted.'}
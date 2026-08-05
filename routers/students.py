from fastapi import APIRouter, Depends, status, HTTPException
from schemas.studentsSchema import StudentsSchema, EditStudentSchema
import psycopg2
from database import get_connection, count_rows
import math


router = APIRouter(prefix='/students')

@router.get('', status_code=status.HTTP_200_OK)
def get_students(search: str = None, limit: int = 4, page: int = 1, filter:str = 'created_at', db = Depends(get_connection)):
    _, cursor = db 
    
    if limit < 2:
        limit = 2
        
    offset = (page - 1) * limit
    
    if filter != 'created_at' and filter != 'first_name':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid filter. Allowed values are: created_at, first_name.')
    
    where_clause = ''
    
    if search:
        where_clause = 'WHERE first_name ILIKE %s'
        search_term = f'%{search}%'
        execute_values = (search_term, limit, offset)
    else:
        execute_values = (limit, offset)
        
    cursor.execute(f'SELECT * FROM students {where_clause} ORDER BY {filter} LIMIT %s OFFSET %s',
        execute_values)
    
    students = cursor.fetchall()
    total_students = count_rows(cursor, 'students', where_clause, search_term if search else '')

    return {
        'students': students,
        'current_page': page,
        'total_pages': math.ceil(total_students / limit)
    }


@router.get('/all', status_code=status.HTTP_200_OK)
def get_all_students(db = Depends(get_connection)):
    _, cursor = db
    
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    
    if students:
        return students
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Students not found.')
    
    
@router.post('/add', status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentsSchema, db = Depends(get_connection)):
    connection , cursor = db 
    
    try:
        cursor.execute('INSERT INTO students (first_name, last_name, age, class_id, tag, current_module) VALUES (%s, %s, %s, %s, %s, %s)',
            (student_data.first_name, student_data.last_name, student_data.age, student_data.class_id, student_data.tag, student_data.current_module))
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
    
    
@router.patch('/edit', status_code=status.HTTP_200_OK)
def edit_student(new_data: EditStudentSchema, db = Depends(get_connection)):
    connection, cursor = db
    clauses = []
    execute_values = []

    if new_data.first_name:
        clauses.append('first_name = %s')
        execute_values.append(new_data.first_name)
    if new_data.last_name:
        clauses.append('last_name = %s')
        execute_values.append(new_data.last_name)
        
    if new_data.current_module:
        clauses.append('current_module = %s')
        execute_values.append(new_data.current_module)
        
    if new_data.tag:
        clauses.append('tag = %s')
        execute_values.append(new_data.tag)
        
    set_clause = ', '.join(clauses)

    try:
        cursor.execute(f'UPDATE students SET {set_clause} WHERE id = %s', (*execute_values, new_data.id))
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student not found')
        
        connection.commit()
    except psycopg2.errors.DataError: 
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid data format')
    
    
@router.delete('/remove/{student_id}', status_code=status.HTTP_200_OK)
def delete_student(student_id: str, db = Depends(get_connection)):
    connection, cursor = db
    
    cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
        
    if cursor.rowcount == 0:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student not found')
    
    connection.commit()
    
    return {'ok': 'Student successfully deleted.'}
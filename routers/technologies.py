from fastapi import APIRouter, Depends, status, HTTPException
from schemas.technologiesSchema import TechnologiesSchema, EditTechnologiesSchema
import psycopg2
from database import get_connection, count_rows
import math

router = APIRouter(prefix='/techs')

@router.get('/all', status_code=status.HTTP_200_OK)
def get_all_techs(page: int = 1 , limit:int = 4, db = Depends(get_connection)):
    _, cursor = db 
    
    if limit < 2:
        limit = 2
        
    offset = (page - 1) * limit
    
    cursor.execute(f'SELECT * FROM technologies ORDER BY created_at LIMIT %s OFFSET %s',
        (limit, offset))
    
    techs = cursor.fetchall()
    total_techs = count_rows(cursor, 'technologies')

    return {
        'techs': techs,
        'current_page': page,
        'total_pages': math.ceil(total_techs / limit)
    }
    

@router.post('/add', status_code=status.HTTP_201_CREATED)
def create_technology(tech_data: TechnologiesSchema, db = Depends(get_connection)):
    connection, cursor = db

    try:
        cursor.execute('INSERT INTO technologies ( name, course_id, tech_icon ) VALUES (%s, %s, %s)',
            (tech_data.name, tech_data.course_id, tech_data.tech_icon))
        
        connection.commit()
        
    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = 'This tech is already registered.')
    
    except psycopg2.errors.ForeignKeyViolation:
        connection.rollback()
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail='Referenced course does not exist.')

    return {'ok': 'Tech successfully registeredd.'}


@router.patch('/edit', status_code=status.HTTP_200_OK)
def edit_tech(new_data: EditTechnologiesSchema, db = Depends(get_connection)):
    connection, cursor = db
    clauses = []
    execute_values = []

    if new_data.name:
        clauses.append('name = %s')
        execute_values.append(new_data.name)
    if new_data.tech_icon:
        clauses.append('tech_icon = %s')
        execute_values.append(new_data.tech_icon)
    if new_data.course_id:
        clauses.append('course_id = %s')
        execute_values.append(new_data.course_id)
        
    set_clause = ', '.join(clauses)

    try:
        cursor.execute(f'UPDATE technologies SET {set_clause} WHERE id = %s', (*execute_values, new_data.id))
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tech not found')
        
        connection.commit()
    except psycopg2.errors.DataError: 
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid data format')
    

@router.delete('/remove/{tech_id}', status_code=status.HTTP_200_OK)
def delete_tech(tech_id: str, db = Depends(get_connection)):
    connection, cursor = db
    
    cursor.execute('DELETE FROM technologies WHERE id = %s', (tech_id,))
        
    if cursor.rowcount == 0:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tech not found')
    
    connection.commit()
    
    return {'ok': 'Tech successfully deleted.'}
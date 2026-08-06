from fastapi import APIRouter, Depends, status, HTTPException
from schemas.technologiesSchema import TechnologiesSchema
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
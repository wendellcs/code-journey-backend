from fastapi import APIRouter, Depends, status, HTTPException
import psycopg2
from database import get_connection


router = APIRouter(prefix='/general')

@router.get('/total', status_code=status.HTTP_200_OK)
def count_registered_data(db = Depends(get_connection)):
    _, cursor = db 
    
    cursor.execute('''
        SELECT
            (SELECT COUNT(*) FROM students) AS total_students,
            (SELECT COUNT(*) FROM technologies) AS total_technologies,
            (SELECT COUNT(*) FROM classes) AS total_classes;
    ''')
    total = cursor.fetchone()
    
    if total:
        return total 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='We could not find data to count.')


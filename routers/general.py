from fastapi import APIRouter, Depends, status, HTTPException
from database import get_connection, count_rows

router = APIRouter(prefix='/general')


@router.get('/total', status_code=status.HTTP_200_OK)
def count_total_data(db = Depends(get_connection)):
    _, cursor = db 
    
    total = {
        'total_students': count_rows(cursor, 'students'),
        'total_technologies': count_rows(cursor, 'technologies'),
        'total_classes': count_rows(cursor, 'classes')
    }
    
    return total


@router.get('/metrics', status_code=status.HTTP_200_OK)
def count_registered_data(db = Depends(get_connection)):
    _, cursor = db 
    
    cursor.execute("SELECT COUNT(*) AS total FROM technologies WHERE created_at > NOW() - INTERVAL '7 days';")
    total = cursor.fetchone()
    
    if total:
        return total 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='We could not find data to count.')
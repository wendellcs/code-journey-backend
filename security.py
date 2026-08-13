from fastapi import Header, HTTPException, status 
import os 

def verify_token(authorization: str = Header(...)):
    if authorization != os.getenv('ACCESS_TOKEN'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.')
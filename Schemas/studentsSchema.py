from pydantic import BaseModel
import uuid

class StudentsSchema(BaseModel):
    first_name: str 
    last_name: str 
    age: int 
    tag: str | None = None
    class_id: uuid.UUID | None = None
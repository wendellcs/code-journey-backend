from pydantic import BaseModel
from typing import Optional
import uuid

class StudentsSchema(BaseModel):
    first_name: str 
    last_name: str 
    current_module: str
    age: int 
    tag: str | None = None
    class_id: uuid.UUID | None = None
    
class EditStudentSchema(BaseModel):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    current_module: Optional[str] = None
    tag: Optional[str] = None
    
class StudentSkillSchema(BaseModel):
    technology_id: uuid.UUID | None = None
    independence_level: int
    notes: str = None 
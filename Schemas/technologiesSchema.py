from pydantic import BaseModel
from typing import Optional
import uuid

class TechnologiesSchema(BaseModel):
    name: str
    course_id: uuid.UUID | None = None
    tech_icon: str
    
    
class EditTechnologiesSchema(BaseModel):
    id: str
    name: Optional[str] = None
    course_id: Optional[str] = None
    tech_icon: Optional[str] = None
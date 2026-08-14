from pydantic import BaseModel, Field
from datetime import time
from typing import Optional

class ClassesSchema(BaseModel):
    module: str 
    day_of_week: str
    class_time: time
    
class EditClassesSchema(BaseModel):
    id: str
    module: Optional[str] = None
    day_of_week: Optional[str] = None
    class_time: Optional[str] = None
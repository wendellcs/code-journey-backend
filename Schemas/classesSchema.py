from pydantic import BaseModel, Field
from datetime import time

class ClassesSchema(BaseModel):
    module: str 
    day_of_week: str
    class_time: time
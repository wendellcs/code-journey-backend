from pydantic import BaseModel
import uuid

class TechnologiesSchema(BaseModel):
    name: str
    course_id: uuid.UUID | None = None
    tech_icon: str
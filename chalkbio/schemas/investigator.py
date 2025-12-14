from pydantic import BaseModel
from datetime import datetime
import uuid

class Investigator(BaseModel):
    investigator_id: uuid.UUID
    name: str
    institution: str | None
    success_rate: float
    influence_score: float

    class Config:
        from_attributes = True
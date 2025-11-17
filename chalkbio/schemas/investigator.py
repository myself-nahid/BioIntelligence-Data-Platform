from pydantic import BaseModel
from datetime import datetime

class Investigator(BaseModel):
    investigator_id: str
    name: str
    institution: str | None
    success_rate: float
    total_trials: int
    last_updated: datetime

    class Config:
        from_attributes = True
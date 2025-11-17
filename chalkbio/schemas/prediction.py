from pydantic import BaseModel
from datetime import datetime

class PredictionResponse(BaseModel):
    trial_id: str
    drug_id: str
    predicted_probability: float
    confidence_lower: float
    confidence_upper: float
    model_version: str
    created_at: datetime

    class Config:
        from_attributes = True
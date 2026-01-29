from pydantic import BaseModel
from datetime import datetime

class ModelPerformanceResponse(BaseModel):
    name: str
    version: str
    trained_on: datetime
    auc: float | None
    calibration_score: float | None
    notes: str | None

    class Config:
        from_attributes = True

class ModelPerformanceResponseWrapper(BaseModel):
    status: str
    message: str
    data: ModelPerformanceResponse
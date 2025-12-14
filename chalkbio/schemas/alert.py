from pydantic import BaseModel
from datetime import datetime
import uuid

class AlertResponse(BaseModel):
    alert_id: uuid.UUID
    title: str
    message: str
    created_at: datetime
    clicked_at: datetime | None

    class Config:
        from_attributes = True
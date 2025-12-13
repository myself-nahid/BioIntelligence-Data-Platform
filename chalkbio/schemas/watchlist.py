from pydantic import BaseModel
from datetime import datetime
import uuid

# Schema for data we expect when a user adds an item
class WatchlistCreate(BaseModel):
    user_id: uuid.UUID
    entity_id: str
    entity_type: str

# Schema for data we will return from the API
class WatchlistResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    entity_id: str
    entity_type: str
    added_at: datetime

    class Config:
        from_attributes = True # Formerly orm_mode = True
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import List

class WatchlistCreate(BaseModel):
    user_id: uuid.UUID
    entity_id: str
    entity_type: str

class WatchlistResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    entity_id: str
    entity_type: str
    added_at: datetime

    class Config:
        from_attributes = True 

class WatchlistCreateWrapper(BaseModel):
    status: str
    message: str
    data: WatchlistResponse


class WatchlistListWrapper(BaseModel):
    status: str
    message: str
    data: List[WatchlistResponse]
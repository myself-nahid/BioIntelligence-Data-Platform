from pydantic import BaseModel, Field
from typing import Dict, Any
import uuid

class UserEventCreate(BaseModel):
    user_id: uuid.UUID
    user_type: str
    event_type: str
    entity_id: str | None = None
    entity_type: str | None = None
    metadata: Dict[str, Any] | None = None
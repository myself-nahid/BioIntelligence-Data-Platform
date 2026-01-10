from pydantic import BaseModel
from .investigator import Investigator

class CollaborationResponse(BaseModel):
    collaborator: Investigator
    collaboration_count: int

    class Config:
        from_attributes = True
        
class CollaborationListWrapper(BaseModel):
    status: str
    message: str
    data: list[CollaborationResponse]
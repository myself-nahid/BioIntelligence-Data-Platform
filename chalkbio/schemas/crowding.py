from pydantic import BaseModel

class CrowdingIndexResponse(BaseModel):
    mechanism_of_action: str
    phase: str
    competitor_count: int
    crowding_risk_score: int

    class Config:
        from_attributes = True
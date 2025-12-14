from fastapi import APIRouter, Depends
from sqlalchemy import text
from typing import List
from sqlalchemy.orm import Session
from ...schemas.crowding import CrowdingIndexResponse
from ..deps import get_db

router = APIRouter()

class CrowdingIndexRecord(CrowdingIndexResponse):
    """Subclass to allow creation from raw SQL row."""
    @classmethod
    def from_orm(cls, row):
        return cls(
            mechanism_of_action=row.mechanism_of_action,
            phase=row.phase,
            competitor_count=row.competitor_count,
            crowding_risk_score=row.crowding_risk_score
        )

@router.get("/crowding/leaderboard", response_model=List[CrowdingIndexResponse])
def get_crowding_leaderboard(db: Session = Depends(get_db)):
    """Retrieves the mechanism crowding index leaderboard."""
    query = text("SELECT * FROM mechanism_crowding ORDER BY crowding_risk_score DESC, competitor_count DESC;")
    results = db.execute(query).fetchall()
    return [CrowdingIndexRecord.from_orm(row) for row in results]
from fastapi import APIRouter, Depends
from sqlalchemy import text
from typing import List
from sqlalchemy.orm import Session
from ...schemas.crowding import CrowdingIndexResponse, CrowdingIndexResponseWrapper
from ..deps import get_db

router = APIRouter()

@router.get(
    "/crowding/leaderboard",
    response_model=CrowdingIndexResponseWrapper
)
def get_crowding_leaderboard(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            mechanism_of_action,
            phase,
            competitor_count,
            crowding_risk_score
        FROM mechanism_crowding
        ORDER BY crowding_risk_score DESC, competitor_count DESC;
    """)

    results = db.execute(query).fetchall()

    data = [
        CrowdingIndexResponse(
            mechanism_of_action=row.mechanism_of_action,
            phase=row.phase,
            competitor_count=row.competitor_count,
            crowding_risk_score=row.crowding_risk_score
        )
        for row in results
    ]

    return {
        "status": "success",
        "message": "Crowding index retrieved successfully",
        "data": data
    }
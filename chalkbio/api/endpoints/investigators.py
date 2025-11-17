from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from ...schemas.investigator import Investigator
from ..deps import get_db

router = APIRouter()

@router.get("/investigators/top", response_model=List[Investigator])
def get_top_investigators(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of top investigators based on their success rate and number of trials.
    """
    # This is a placeholder for the actual database query logic
    # In a real implementation, you would query the 'investigators' table
    # and order by a calculated influence_score or success_rate.
    # For now, we return a mock response.
    mock_investigators = [
        Investigator(investigator_id="uuid-1", name="Dr. Jane Smith", institution="PharmaCo", success_rate=0.82, total_trials=25, last_updated="2025-11-17T12:00:00Z"),
        Investigator(investigator_id="uuid-2", name="Dr. John Doe", institution="BioGen", success_rate=0.75, total_trials=18, last_updated="2025-11-17T12:00:00Z")
    ]
    return mock_investigators[:limit]
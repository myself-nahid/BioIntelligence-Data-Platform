from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from ...schemas.investigator import Investigator as InvestigatorSchema, InvestigatorWrapper
from ...models.orm import Investigator as InvestigatorModel
from ..deps import get_db

router = APIRouter()

@router.get("/investigators/top", response_model=InvestigatorWrapper)
def get_top_investigators(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieves a list of top investigators based on their influence score."""
    top_investigators = db.query(InvestigatorModel).order_by(
        InvestigatorModel.influence_score.desc()
    ).limit(limit).all()
    return {
        "status": "success",
        "message": "Top investigators retrieved successfully",
        "data": top_investigators
    }
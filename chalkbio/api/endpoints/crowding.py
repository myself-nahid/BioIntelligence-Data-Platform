from fastapi import APIRouter, Depends
from sqlalchemy import text
from typing import List
from sqlalchemy.orm import Session
from ...schemas.crowding import CrowdingIndexResponse, CrowdingIndexResponseWrapper
from ..deps import get_db
from fastapi import HTTPException, status

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

@router.get(
    "/crowding/mechanism/{moa}",
    response_model=CrowdingIndexResponseWrapper
)
def get_crowding_by_mechanism(
    moa: str,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT 
            mechanism_of_action,
            phase,
            competitor_count,
            crowding_risk_score
        FROM mechanism_crowding
        WHERE mechanism_of_action = :moa;
    """)

    results = db.execute(query, {"moa": moa}).mappings().all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Mechanism of action not found in the crowding index."
        )

    data = [
        CrowdingIndexResponse(**row)
        for row in results
    ]

    return {
        "status": "success",
        "message": "Crowding index retrieved successfully",
        "data": data
    }

@router.get(
    "/crowding/drug/{drug_id}",
    response_model=CrowdingIndexResponseWrapper
)
def get_crowding_for_drug(
    drug_id: str,
    db: Session = Depends(get_db)
):
    # Step 1: Find trial mechanism & phase
    trial_query = text("""
        SELECT mechanism_of_action, phase
        FROM trials
        WHERE trial_id = :drug_id
        LIMIT 1;
    """)

    trial = db.execute(trial_query, {"drug_id": drug_id}).mappings().first()

    if not trial:
        raise HTTPException(
            status_code=404,
            detail="Drug/Trial ID not found."
        )

    # Step 2: Find crowding index
    crowding_query = text("""
        SELECT 
            mechanism_of_action,
            phase,
            competitor_count,
            crowding_risk_score
        FROM mechanism_crowding
        WHERE mechanism_of_action = :moa
          AND phase = :phase
        LIMIT 1;
    """)

    crowding = db.execute(
        crowding_query,
        {
            "moa": trial["mechanism_of_action"],
            "phase": trial["phase"]
        }
    ).mappings().first()

    if not crowding:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No crowding index data found for mechanism "
                f"'{trial['mechanism_of_action']}' in phase '{trial['phase']}'."
            )
        )

    return {
        "status": "success",
        "message": "Crowding index retrieved successfully",
        "data": [CrowdingIndexResponse(**crowding)]
    }
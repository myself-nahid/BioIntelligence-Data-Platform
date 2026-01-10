from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
import uuid

from ...schemas.investigator import Investigator as InvestigatorSchema, InvestigatorWrapper
from ...schemas.collaboration import CollaborationResponse, CollaborationListWrapper
from ...schemas.common import ResponseWrapper
from ...models.orm import Investigator as InvestigatorModel, Collaboration as CollaborationModel

from ..deps import get_db

router = APIRouter(redirect_slashes=True)

def find_investigator_or_404(db: Session, investigator_id: uuid.UUID) -> InvestigatorModel:
    investigator = db.query(InvestigatorModel).filter(InvestigatorModel.investigator_id == investigator_id).first()
    if not investigator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigator not found")
    return investigator

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

@router.get("/investigators/{investigator_id}", response_model=ResponseWrapper[InvestigatorSchema])
def get_investigator_details(
    investigator_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    investigator = find_investigator_or_404(db, investigator_id)
    return {
        "status": "success",
        "message": "Investigator details retrieved successfully",
        "data": investigator
    }

@router.get(
    "/investigators/{investigator_id}/network",
    response_model=CollaborationListWrapper
)
def get_investigator_network(
    investigator_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    find_investigator_or_404(db, investigator_id)
    collaborations = db.query(CollaborationModel).filter(
        or_(
            CollaborationModel.investigator_a_id == investigator_id,
            CollaborationModel.investigator_b_id == investigator_id
        )
    ).all()
    network = []
    for collab in collaborations:
        collaborator_id = (
            collab.investigator_b_id
            if collab.investigator_a_id == investigator_id
            else collab.investigator_a_id
        )
        collaborator = find_investigator_or_404(db, collaborator_id)
        network.append(
            CollaborationResponse(
                collaborator=collaborator,
                collaboration_count=collab.collaboration_count
            )
        )
    return {
        "status": "success",
        "message": "Investigator collaboration network retrieved successfully",
        "data": network
    }
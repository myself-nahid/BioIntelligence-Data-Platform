from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid
from ...schemas.alert import AlertResponse
from ...models.orm import Alert

from ..deps import get_db

router = APIRouter(redirect_slashes=True)

@router.get("/alerts", response_model=List[AlertResponse])
def get_user_alerts(
    user_id: uuid.UUID = Query(..., description="The UUID of the user to retrieve alerts for"),
    db: Session = Depends(get_db)
):
    """Retrieves all alerts for a given user."""
    alerts = db.query(Alert).filter(Alert.user_id == user_id).order_by(Alert.created_at.desc()).all()
    return alerts
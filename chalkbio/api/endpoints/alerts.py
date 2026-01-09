from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from ...schemas.alert import AlertResponseWrapper
from ...models.orm import Alert
from ..deps import get_db
from fastapi import HTTPException, status, Response
from datetime import datetime, timezone

router = APIRouter(redirect_slashes=True)

def find_alert_or_404(db: Session, alert_id: uuid.UUID) -> Alert:
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert

@router.get("/alerts", response_model=AlertResponseWrapper)
def get_user_alerts(
    user_id: uuid.UUID = Query(..., description="The UUID of the user to retrieve alerts for"),
    db: Session = Depends(get_db)
):
    alerts = (
        db.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "message": "Alerts retrieved successfully",
        "data": alerts
    }

@router.post("/alerts/{alert_id}/open", response_model=AlertResponseWrapper)
def mark_alert_opened(alert_id: uuid.UUID, db: Session = Depends(get_db)):
    alert = find_alert_or_404(db, alert_id)
    if not alert.opened_at:
        alert.opened_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)

    return {
        "status": "success",
        "message": "Alert marked as opened",
        "data": [alert]  
    }

@router.post("/alerts/{alert_id}/click", response_model=AlertResponseWrapper)
def mark_alert_clicked(alert_id: uuid.UUID, db: Session = Depends(get_db)):
    alert = find_alert_or_404(db, alert_id)

    now = datetime.now(timezone.utc)
    if not alert.opened_at:
        alert.opened_at = now
    if not alert.clicked_at:
        alert.clicked_at = now

    db.commit()
    db.refresh(alert)

    return {
        "status": "success",
        "message": "Alert marked as clicked",
        "data": [alert]  
    }

@router.delete("/alerts/{alert_id}", response_model=AlertResponseWrapper)
def dismiss_alert(alert_id: uuid.UUID, db: Session = Depends(get_db)):
    alert = find_alert_or_404(db, alert_id)
    if not alert.dismissed_at:
        alert.dismissed_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "status": "success",
        "message": "Alert dismissed successfully",
        "data": []  
    }
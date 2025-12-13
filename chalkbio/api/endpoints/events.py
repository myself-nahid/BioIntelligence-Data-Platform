from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...schemas.user_event import UserEventCreate
from ...models.orm import UserEvent
from ..deps import get_db

router = APIRouter()

@router.post("/events", status_code=status.HTTP_201_CREATED)
def log_user_event(
    event: UserEventCreate,
    db: Session = Depends(get_db)
):
    """
    Receives and logs a single user event to the database.
    """
    # Convert the Pydantic model to a dictionary
    event_data = event.model_dump()
    
    # Handle the 'metadata' name clash
    if 'metadata' in event_data:
        event_data['metadata_'] = event_data.pop('metadata')

    # Create a new UserEvent database object from the modified dictionary
    db_event = UserEvent(**event_data)
    
    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        db.rollback()
        # In production, you would log the error `e`
        print(f"Error logging event: {e}") # Added for debugging
        raise HTTPException(
            status_code=500,
            detail="Failed to log user event."
        )
        
    return {"status": "success", "event_id": db_event.event_id}
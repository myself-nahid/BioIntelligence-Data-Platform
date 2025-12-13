from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from ...schemas.watchlist import WatchlistCreate, WatchlistResponse
from ...models.orm import Watchlist
from ..deps import get_db

router = APIRouter()

@router.post("/watchlists", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    item: WatchlistCreate,
    db: Session = Depends(get_db)
):
    """
    Adds a new entity to a user's watchlist.
    """
    db_item = Watchlist(**item.model_dump())
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item to watchlist: {e}"
        )
        
    return db_item

@router.get("/watchlists", response_model=List[WatchlistResponse])
def get_user_watchlist(
    user_id: uuid.UUID = Query(..., description="The UUID of the user whose watchlist to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieves all active items in a user's watchlist.
    """
    watchlist_items = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.removed_at == None
    ).all()
    
    return watchlist_items
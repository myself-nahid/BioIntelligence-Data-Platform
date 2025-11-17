from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas.prediction import PredictionResponse
from ...models import predict
from ..deps import get_db

router = APIRouter()

@router.get("/predictions/trial/{trial_id}", response_model=PredictionResponse)
def predict_trial_success(trial_id: str, db: Session = Depends(get_db)):
    """
    Predicts the Phase II->III success probability for a given trial ID.
    - **trial_id**: The unique identifier for the clinical trial (e.g., NCT123456).
    """
    try:
        # In a real app, this would fetch features for the trial_id
        # and then pass them to the prediction function.
        # We will simulate this for now.
        prediction_data = predict.get_prediction_for_trial(db=db, trial_id=trial_id)

        if not prediction_data:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction available for trial ID: {trial_id}"
            )
        return prediction_data
    except Exception as e:
        # In production, you would log the error `e`
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while making a prediction."
        )
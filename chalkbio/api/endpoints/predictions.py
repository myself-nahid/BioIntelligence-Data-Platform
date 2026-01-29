from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas.prediction import PredictionResponse, PredictionResponseWrapper
from ...models import predict
from ..deps import get_db
from ...schemas.model_performance import ModelPerformanceResponse, ModelPerformanceResponseWrapper
from ...models.orm import MLModel
from fastapi import status

router = APIRouter()

@router.get("/predictions/trial/{trial_id}", response_model=PredictionResponseWrapper)
def predict_trial_success(trial_id: str, db: Session = Depends(get_db)):
    """
    Predicts the Phase II->III success probability for a given trial ID.
    - **trial_id**: The unique identifier for the clinical trial (e.g., NCT123456).
    """
    try:
        prediction_data = predict.get_prediction_for_trial(db=db, trial_id=trial_id)

        if not prediction_data:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction available for trial ID: {trial_id}"
            )
        return {"status": "success", "message": "Prediction made successfully", "data": prediction_data}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while making a prediction."
        )
    
@router.get("/predictions/model/performance", response_model=ModelPerformanceResponseWrapper)
def get_model_performance(db: Session = Depends(get_db)):
    """
    Retrieves the performance metrics for the latest trained model.
    """
    latest_model = db.query(MLModel).order_by(MLModel.trained_on.desc()).first()

    if not latest_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No model performance data found in the database."
        )
    
    return {
        "status": "success",
        "message": "Model performance retrieved successfully",
        "data": latest_model
    }
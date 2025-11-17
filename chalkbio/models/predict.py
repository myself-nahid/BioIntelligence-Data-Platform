import pickle
import json
import pandas as pd
from sqlalchemy.orm import Session

# Define paths for model artifacts
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/trial_success_predictor_v1.0.pkl"
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns.json"

def load_prediction_assets():
    """Loads the model and the list of training columns from disk."""
    model = None
    training_columns = None
    try:
        with open(MODEL_ARTIFACT_PATH, "rb") as f:
            model = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_ARTIFACT_PATH}")

    try:
        with open(TRAINING_COLUMNS_PATH, "r") as f:
            training_columns = json.load(f)
    except FileNotFoundError:
        print(f"Error: Training columns file not found at {TRAINING_COLUMNS_PATH}")

    return model, training_columns

# Load assets once when the application starts
model, training_columns = load_prediction_assets()

def get_prediction_for_trial(db: Session, trial_id: str):
    """
    Fetches trial features, preprocesses them consistently, and returns a prediction.
    """
    if not model or not training_columns:
        raise RuntimeError("Model or training columns are not loaded. Cannot make predictions.")

    # --- 1. SIMULATED FEATURE FETCHING ---
    # In a real app, you would query the DB for the raw features of the trial_id.
    # We will mock this data.
    raw_trial_data = {
        'phase': 'Phase II',
        'indication': 'Oncology',
        'sponsor_size': 750,
        'investigator_success_rate': 0.78,
        'mechanism_crowding_score': 50
    }
    
    # --- 2. PREPARE THE DATAFRAME ---
    # Create a DataFrame from the single prediction request
    predict_df = pd.DataFrame([raw_trial_data])

    # --- 3. TRANSFORM DATA CONSISTENTLY ---
    # One-hot encode the categorical features
    predict_df_processed = pd.get_dummies(predict_df, columns=['phase', 'indication'], drop_first=False)

    # --- 4. ALIGN COLUMNS ---
    # This is the CRITICAL step.
    # Reindex the prediction DataFrame to match the training columns exactly.
    # - It adds any missing columns (and fills them with 0).
    # - It removes any columns that were not in the training data.
    # - It orders the columns correctly.
    predict_df_aligned = predict_df_processed.reindex(columns=training_columns, fill_value=0)

    # --- 5. MAKE PREDICTION ---
    probability = model.predict_proba(predict_df_aligned)[0, 1]

    # Return data in the Pydantic schema format
    return {
        "trial_id": trial_id,
        "drug_id": "DRUG-XYZ",
        "predicted_probability": round(probability, 4),
        "confidence_lower": round(max(0, probability - 0.12), 4),
        "confidence_upper": round(min(1, probability + 0.12), 4),
        "model_version": "v1.0",
        "created_at": "2025-11-17T15:00:00Z"
    }
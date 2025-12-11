import pickle
import json
import pandas as pd
from sqlalchemy.orm import Session

# Import our new feature engineering function
from .feature_engineering import get_text_embeddings

# Define paths for the new v2 model artifacts
MODEL_NAME = "trial_success_predictor_hybrid"
MODEL_VERSION = "v2.0"
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns_v2.json"

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
    Fetches trial features, engineers them using the hybrid approach, and returns a prediction.
    """
    if not model or not training_columns:
        raise RuntimeError("Hybrid model or training columns are not loaded. Cannot make predictions.")

    # 1. SIMULATED FEATURE FETCHING (Now includes text)
    raw_trial_data = {
        'trial_description': "A Phase II study to determine the antitumor activity of Drug X in metastatic breast cancer.",
        'phase': 'Phase II',
        'indication': 'Oncology',
        'sponsor_size': 750,
        'investigator_success_rate': 0.78,
        'mechanism_crowding_score': 50
    }
    predict_df = pd.DataFrame([raw_trial_data])

    # 2. ENGINEER FEATURES (Identical to training)
    
    # a) Structured Features
    structured_features_df = pd.get_dummies(
        predict_df[['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']],
        columns=['phase', 'indication'],
        drop_first=False
    )
    
    # b) Text Features
    text_embeddings_df = get_text_embeddings(predict_df['trial_description'])

    # c) Combine Features
    predict_df_processed = pd.concat([structured_features_df, text_embeddings_df], axis=1)

    # 3. ALIGN COLUMNS (Critical step remains the same)
    predict_df_aligned = predict_df_processed.reindex(columns=training_columns, fill_value=0)

    # 4. MAKE PREDICTION
    probability = model.predict_proba(predict_df_aligned)[0, 1]

    # Return data
    return {
        "trial_id": trial_id,
        "drug_id": "DRUG-XYZ",
        "predicted_probability": round(probability, 4),
        "confidence_lower": round(max(0, probability - 0.12), 4),
        "confidence_upper": round(min(1, probability + 0.12), 4),
        "model_version": MODEL_VERSION, # Report the new version
        "created_at": "2025-11-17T15:00:00Z"
    }
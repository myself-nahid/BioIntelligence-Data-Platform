import pickle
import json
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from .feature_engineering import get_text_embeddings

# Define paths for the new v2 model artifacts
MODEL_NAME = "trial_success_predictor_hybrid"
MODEL_VERSION = "v2.0"
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns_v2.json"
CATEGORIES_PATH = f"{MODEL_ARTIFACT_DIR}/categories.json"

def load_prediction_assets():
    """Loads model, columns, AND categories from disk."""
    # --- THIS IS THE FIX: Initialize all variables at the top ---
    model, training_columns, categories = None, None, None
    # -----------------------------------------------------------

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

    try:
        with open(CATEGORIES_PATH, "r") as f:
            categories = json.load(f)
    except FileNotFoundError:
        print(f"Error: Categories file not found at {CATEGORIES_PATH}")

    return model, training_columns, categories
# Load assets once when the module is imported
model, training_columns, categories = load_prediction_assets()

def get_prediction_for_trial(db: Session, trial_id: str):
    """
    Fetches REAL trial features, engineers them, and returns a prediction.
    """
    if not model or not training_columns:
        raise RuntimeError("Hybrid model or training columns are not loaded.")

    # 1. FETCH REAL FEATURES from the database
    query = text("""
    SELECT
        t.trial_id, t.trial_description, t.phase, t.indication, t.sponsor_size,
        i.success_rate as investigator_success_rate,
        mc.crowding_risk_score as mechanism_crowding_score
    FROM trials t
    LEFT JOIN investigators i ON t.investigator_id = i.investigator_id
    LEFT JOIN mechanism_crowding mc ON t.mechanism_of_action = mc.mechanism_of_action AND t.phase = mc.phase
    WHERE t.trial_id = :trial_id
    LIMIT 1;
    """)
    
    result = db.execute(query, {'trial_id': trial_id}).mappings().first()

    if not result:
        return None # Let the API handle the 404

    # Convert SQL row to a DataFrame, filling missing values
    predict_df = pd.DataFrame([result]).fillna(0)
    for col, cats in categories.items():
        if col in predict_df.columns:
            predict_df[col] = pd.Categorical(predict_df[col], categories=cats)

    # 2. ENGINEER FEATURES (Identical to training)
    
    # a) Structured Features
    structured_features_df = pd.get_dummies(
        predict_df[['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']],
        columns=['phase', 'indication'], # Explicitly name the columns to encode
        drop_first=False
    )
    # ------------------------------------
    
    # b) Text Features
    text_embeddings_df = get_text_embeddings(predict_df['trial_description'])

    # c) Combine Features
    # --- THIS IS THE FIX ---
    # Reset the index on both DataFrames to ensure they align perfectly
    structured_features_df.reset_index(drop=True, inplace=True)
    text_embeddings_df.reset_index(drop=True, inplace=True)
    # ------------------------------------
    predict_df_processed = pd.concat([structured_features_df, text_embeddings_df], axis=1)

    # 3. ALIGN COLUMNS (This is now our failsafe)
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
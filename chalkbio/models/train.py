# from email.mime import text
import pandas as pd
import pickle
import os
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from ..core.db import SessionLocal
import pandas as pd
from sqlalchemy import text

# Import our new feature engineering function
from .feature_engineering import get_text_embeddings

MODEL_NAME = "trial_success_predictor_hybrid"
MODEL_VERSION = "v2.0" # New model version
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns_v2.json"
CATEGORIES_PATH = f"{MODEL_ARTIFACT_DIR}/categories.json"

def run_training_pipeline():
    """
    The main function to execute the HYBRID model training pipeline using REAL data.
    """
    print("Starting HYBRID model training pipeline with database data...")
    db = SessionLocal()
    
    try:
        # --- THIS IS THE FIX: Refresh the materialized view before querying ---
        print("Refreshing mechanism_crowding view to ensure data is fresh...")
        db.execute(text("REFRESH MATERIALIZED VIEW mechanism_crowding;"))
        db.commit()
        print("View refreshed.")
        # -------------------------------------------------------------------

        # 1. Load Data from the database
        query = """
        SELECT
            t.trial_id, t.trial_description, t.phase, t.indication, t.sponsor_size, t.outcome,
            i.success_rate as investigator_success_rate,
            mc.crowding_risk_score as mechanism_crowding_score
        FROM trials t
        LEFT JOIN investigators i ON t.investigator_id = i.investigator_id
        LEFT JOIN mechanism_crowding mc ON t.mechanism_of_action = mc.mechanism_of_action AND t.phase = mc.phase
        WHERE t.phase = 'Phase II' AND t.outcome IS NOT NULL;
        """
        df = pd.read_sql(query, db.connection())
    finally:
        db.close()

    if df.empty:
        print("No training data found in the database. Aborting training.")
        return

    # Convert outcome to target variable
    df['target'] = df['outcome'].apply(lambda x: 1 if x == 'Success' else 0)
    df.fillna(0, inplace=True) # Simple imputation for missing data
    df['phase'] = pd.Categorical(df['phase'])
    df['indication'] = pd.Categorical(df['indication'])

    # Store the categories for each column
    categories = {
        'phase': df['phase'].cat.categories.tolist(),
        'indication': df['indication'].cat.categories.tolist()
    }
    with open(CATEGORIES_PATH, 'w') as f:
        json.dump(categories, f)
    print(f"Categories saved to {CATEGORIES_PATH}")

    # 2. Engineer Features
    
    # a) Structured Features (same as before)
    structured_features_df = pd.get_dummies(
        df[['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']],
        columns=['phase', 'indication'], # Explicitly name the columns to encode
        drop_first=False
    )
    # ------------------------------------

     # b) Text Features
    text_embeddings_df = get_text_embeddings(df['trial_description'])

    # c) Combine Features
    X = pd.concat([structured_features_df, text_embeddings_df], axis=1)
    y = df['target']

    # 3. Save Training Columns (Critical for prediction)
    training_columns = X.columns.tolist()
    with open(TRAINING_COLUMNS_PATH, 'w') as f:
        json.dump(training_columns, f)
    print(f"Training columns (v2) saved to {TRAINING_COLUMNS_PATH}")

    # --- THIS IS THE FIX ---
    # 4. Train Model on the FULL dataset
    # With a very small seed dataset, we will train on all of it.
    # A train/test split is only meaningful with more data.
    print(f"Training model on {len(X)} samples...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X, y)

    # We can't calculate a true test accuracy, so we'll check training accuracy instead.
    # This should be high (likely 1.0) and confirms the model is learning.
    train_accuracy = model.score(X, y)
    print(f"Hybrid Model training accuracy: {train_accuracy:.4f}")
    # -------------------------

    # 5. Save Model Artifact
    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    with open(MODEL_ARTIFACT_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Hybrid Model artifact saved to {MODEL_ARTIFACT_PATH}")

if __name__ == "__main__":
    run_training_pipeline()
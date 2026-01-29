import pandas as pd
import pickle
import os
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sqlalchemy import text
from datetime import datetime 

from ..core.db import SessionLocal
from .feature_engineering import get_text_embeddings
from .evaluate import evaluate_model
from ..models.orm import MLModel

MODEL_NAME = "trial_success_predictor_hybrid"
MODEL_VERSION = "v2.0"
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns_v2.json"
CATEGORIES_PATH = f"{MODEL_ARTIFACT_DIR}/categories.json"

def run_training_pipeline():
    """
    The main function to execute the HYBRID model training pipeline using REAL data,
    evaluate its performance, and save the results.
    """
    print("Starting HYBRID model training pipeline with database data...")
    db = SessionLocal()
    
    try:
        print("Refreshing mechanism_crowding view to ensure data is fresh...")
        db.execute(text("REFRESH MATERIALIZED VIEW mechanism_crowding;"))
        db.commit()
        print("View refreshed.")
        
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

        if df.empty:
            print("No training data found in the database. Aborting training.")
            return

        df['target'] = df['outcome'].apply(lambda x: 1 if x == 'Success' else 0)
        df.fillna(0, inplace=True)
        df['phase'] = pd.Categorical(df['phase'])
        df['indication'] = pd.Categorical(df['indication'])
        categories = {'phase': df['phase'].cat.categories.tolist(),'indication': df['indication'].cat.categories.tolist()}
        with open(CATEGORIES_PATH, 'w') as f: json.dump(categories, f)
        print(f"Categories saved to {CATEGORIES_PATH}")

        structured_features_df = pd.get_dummies(df[['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']], columns=['phase', 'indication'], drop_first=False)
        text_embeddings_df = get_text_embeddings(df['trial_description'])
        structured_features_df.reset_index(drop=True, inplace=True)
        text_embeddings_df.reset_index(drop=True, inplace=True)
        X = pd.concat([structured_features_df, text_embeddings_df], axis=1)
        y = df['target']
        
        training_columns = X.columns.tolist()
        with open(TRAINING_COLUMNS_PATH, 'w') as f: json.dump(training_columns, f)
        print(f"Training columns (v2) saved to {TRAINING_COLUMNS_PATH}")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)

        print("Evaluating model performance...")
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        metrics = evaluate_model(y_test, y_pred_proba)

        os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
        with open(MODEL_ARTIFACT_PATH, 'wb') as f: pickle.dump(model, f)
        print(f"Hybrid Model artifact saved to {MODEL_ARTIFACT_PATH}")

        print("Saving model performance to database...")
        existing_model_entry = db.query(MLModel).filter_by(name=MODEL_NAME, version=MODEL_VERSION).first()
        if existing_model_entry:
            existing_model_entry.trained_on = datetime.utcnow() # Update timestamp
            existing_model_entry.auc = metrics['auc']
            existing_model_entry.calibration_score = metrics['calibration_score']
            existing_model_entry.artifact_path = MODEL_ARTIFACT_PATH
            existing_model_entry.notes = f"Retrained on {len(X)} samples. Test metrics on {len(X_test)} samples."
        else:
            new_model_entry = MLModel(
                name=MODEL_NAME,
                version=MODEL_VERSION,
                trained_on=datetime.utcnow(), 
                auc=metrics['auc'],
                calibration_score=metrics['calibration_score'],
                artifact_path=MODEL_ARTIFACT_PATH,
                notes=f"Trained on {len(X)} samples. Test metrics on {len(X_test)} samples."
            )
            db.add(new_model_entry)
        
        db.commit()
        print("Performance metrics saved.")

    finally:
        db.close()

if __name__ == "__main__":
    run_training_pipeline()
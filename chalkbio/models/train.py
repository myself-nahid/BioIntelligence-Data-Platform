import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_NAME = "trial_success_predictor"
MODEL_VERSION = "v1.0"
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"

def run_training_pipeline():
    """
    The main function to execute the model training pipeline.
    This would be called by the weekly Celery job.
    """
    print("Starting model training pipeline...")

    # 1. Load Data
    # In a real app, this would be a SQL query:
    # df = pd.read_sql("SELECT ...", db_connection)
    # For now, we create a mock DataFrame.
    data = {
        'phase': ['Phase II'] * 100,
        'indication': ['Oncology', 'Cardiology'] * 50,
        'sponsor_size': [500, 1000] * 50,
        'investigator_success_rate': [0.8, 0.65, 0.77, 0.82] * 25,
        'mechanism_crowding_score': [60, 80, 40, 20] * 25,
        'target': [1, 0, 1, 1, 0] * 20
    }
    df = pd.DataFrame(data)

    # 2. Preprocess Data
    features = ['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']
    target = 'target'
    X = pd.get_dummies(df[features], drop_first=True)
    y = df[target]

    # 3. Train Model (Using simple train/test split instead of TimeSeriesSplit for simplicity here)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # 4. Evaluate Model
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.4f}")
    # In a real app, you would calculate AUC, calibration, etc. and save to ml_models table.

    # 5. Save Model Artifact
    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    with open(MODEL_ARTIFACT_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model artifact saved to {MODEL_ARTIFACT_PATH}")

# This allows running the script directly for testing
if __name__ == "__main__":
    run_training_pipeline()
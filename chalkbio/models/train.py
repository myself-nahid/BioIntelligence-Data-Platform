import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_NAME = "trial_success_predictor"
MODEL_VERSION = "v1.0"
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"
# --- ADD THIS LINE ---
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns.json"

def run_training_pipeline():
    """
    The main function to execute the model training pipeline.
    """
    print("Starting model training pipeline...")

    data = {
        'phase': ['Phase II'] * 100,
        'indication': ['Oncology', 'Cardiology'] * 50,
        'sponsor_size': [500, 1000] * 50,
        'investigator_success_rate': [0.8, 0.65, 0.77, 0.82] * 25,
        'mechanism_crowding_score': [60, 80, 40, 20] * 25,
        'target': [1, 0, 1, 1, 0] * 20
    }
    df = pd.DataFrame(data)

    features = ['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']
    target = 'target'
    X = pd.get_dummies(df[features], columns=['phase', 'indication'], drop_first=False) # Use columns parameter
    y = df[target]
    
    # --- ADD THESE LINES TO SAVE THE COLUMNS ---
    # Save the column names and order to a file
    training_columns = X.columns.tolist()
    with open(TRAINING_COLUMNS_PATH, 'w') as f:
        import json
        json.dump(training_columns, f)
    print(f"Training columns saved to {TRAINING_COLUMNS_PATH}")
    # -------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.4f}")

    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    with open(MODEL_ARTIFACT_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model artifact saved to {MODEL_ARTIFACT_PATH}")

if __name__ == "__main__":
    run_training_pipeline()
import pandas as pd
import pickle
import os
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Import our new feature engineering function
from .feature_engineering import get_text_embeddings

MODEL_NAME = "trial_success_predictor_hybrid"
MODEL_VERSION = "v2.0" # New model version
MODEL_ARTIFACT_DIR = "./models_volume"
MODEL_ARTIFACT_PATH = f"{MODEL_ARTIFACT_DIR}/{MODEL_NAME}_{MODEL_VERSION}.pkl"
TRAINING_COLUMNS_PATH = f"{MODEL_ARTIFACT_DIR}/training_columns_v2.json"

def run_training_pipeline():
    """
    The main function to execute the HYBRID model training pipeline.
    """
    print("Starting HYBRID model training pipeline...")

    # 1. Load Data (Now includes a text column)
    # In a real app, this would be a SQL query.
    data = {
        'trial_description': [
            "A study to evaluate the efficacy of Drug A in patients with non-small cell lung cancer.",
            "Phase II trial of Compound B for the treatment of moderate to severe plaque psoriasis.",
            "Investigating the safety and tolerability of Agent C in healthy adult volunteers.",
            "Efficacy and safety study of Drug D versus placebo for major depressive disorder.",
            # ... add many more examples
        ] * 25,
        'phase': ['Phase II'] * 100,
        'indication': ['Oncology', 'Dermatology', 'Healthy', 'Psychiatry'] * 25,
        'sponsor_size': [500, 1000, 50, 2000] * 25,
        'investigator_success_rate': [0.8, 0.65, 0.9, 0.77] * 25,
        'mechanism_crowding_score': [60, 80, 20, 40] * 25,
        'target': [1, 0, 0, 1] * 25 # 1 for success, 0 for failure
    }
    df = pd.DataFrame(data)

    # 2. Engineer Features
    
    # a) Structured Features (same as before)
    structured_features_df = pd.get_dummies(
        df[['phase', 'indication', 'sponsor_size', 'investigator_success_rate', 'mechanism_crowding_score']],
        columns=['phase', 'indication'],
        drop_first=False
    )
    
    # b) Text Features (THE NEW STEP)
    text_embeddings_df = get_text_embeddings(df['trial_description'])

    # c) Combine Features
    X = pd.concat([structured_features_df, text_embeddings_df], axis=1)
    y = df['target']

    # 3. Save Training Columns (Critical for prediction)
    training_columns = X.columns.tolist()
    with open(TRAINING_COLUMNS_PATH, 'w') as f:
        json.dump(training_columns, f)
    print(f"Training columns (v2) saved to {TRAINING_COLUMNS_PATH}")

    # 4. Train Model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"Hybrid Model accuracy: {accuracy:.4f}")

    # 5. Save Model Artifact
    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    with open(MODEL_ARTIFACT_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Hybrid Model artifact saved to {MODEL_ARTIFACT_PATH}")

if __name__ == "__main__":
    run_training_pipeline()
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_recall_curve
import numpy as np

def evaluate_model(y_true: np.ndarray, y_pred_proba: np.ndarray):
    """
    Calculates and prints key performance metrics for the classification model.
    
    Returns:
        A dictionary of performance metrics.
    """
    auc = roc_auc_score(y_true, y_pred_proba)
    # Higher is better for calibration
    calibration = 1 - brier_score_loss(y_true, y_pred_proba)
    
    metrics = {
        "auc": auc,
        "calibration_score": calibration
    }
    
    print(f"Model Performance Metrics:")
    print(f"  - AUC: {auc:.4f}")
    print(f"  - Calibration Score: {calibration:.4f}")
    
    # In a real scenario, you might also log precision/recall values
    # or save a plot of the PR curve.
    
    return metrics
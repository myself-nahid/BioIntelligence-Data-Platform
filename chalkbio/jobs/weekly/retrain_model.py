# --- CHANGE THIS LINE ---
from ...core.celery_app import celery_app
from ...models import train

# --- AND CHANGE THIS LINE ---
@celery_app.task
def retrain_trial_success_model():
    """
    Celery task to trigger the weekly model retraining pipeline.
    """
    print("Starting weekly model retraining job...")
    try:
        train.run_training_pipeline()
        print("Model retraining completed successfully.")
        return "Model retrained."
    except Exception as e:
        print(f"Model retraining failed: {e}")
        # Here you would add Slack alerting for failures
        raise
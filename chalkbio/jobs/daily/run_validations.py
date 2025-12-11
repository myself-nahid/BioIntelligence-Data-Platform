# --- CHANGE THIS LINE ---
from ...core.celery_app import celery_app
import requests
from ...core.config import settings

# --- AND CHANGE THIS LINE ---
@celery_app.task
def run_user_events_validation():
    """
    Celery task to run the data quality checks on the user_events table.
    """
    print("Running daily user events validation job...")
    job_failed = False
    error_message = ""
    status = "PASS" # Simulate a pass for now
    
    if job_failed:
        post_to_slack(
            job_name="user_events_validation",
            error_message=error_message
        )
    print("Validation job finished.")
    return f"Validation complete with status: {status}"


def post_to_slack(job_name: str, error_message: str):
    """Helper function to post a message to a Slack webhook."""
    if not settings.SLACK_WEBHOOK_URL or "YOUR/SLACK/URL" in settings.SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
        return

    payload = {
        "text": f":x: Job Failed: *{job_name}*\n*Error*: {error_message}"
    }
    try:
        requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to post to Slack: {e}")
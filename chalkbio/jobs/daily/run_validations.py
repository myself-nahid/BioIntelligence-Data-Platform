from ...main import celery
import requests
from ...core.config import settings

@celery.task
def run_user_events_validation():
    """
    Celery task to run the data quality checks on the user_events table.
    In a real app, this would connect to the DB, run the SQL queries
    from the guide, and post to Slack on failure.
    """
    print("Running daily user events validation job...")
    # Simulated failure
    job_failed = False
    error_message = ""

    # --- SIMULATED LOGIC ---
    # 1. INSERT INTO job_run_logs...
    # 2. Run the main validation query from the guide...
    #    - `INSERT INTO data_quality_logs... SELECT ... FROM user_events...`
    # 3. Check the status from data_quality_logs.
    #    - If status is 'FAIL', set job_failed = True
    # 4. UPDATE job_run_logs with completion status.
    
    status = "FAIL" # Simulate a failure for demonstration
    if status == 'FAIL':
        job_failed = True
        error_message = "Validation failed: Found 5 missing user_ids."

    if job_failed:
        post_to_slack(
            job_name="user_events_validation",
            error_message=error_message
        )
    print("Validation job finished.")
    return "Validation complete."


def post_to_slack(job_name: str, error_message: str):
    """Helper function to post a message to a Slack webhook."""
    if not settings.SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
        return

    payload = {
        "text": f":x: Job Failed: *{job_name}*\n*Error*: {error_message}"
    }
    try:
        requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to post to Slack: {e}")
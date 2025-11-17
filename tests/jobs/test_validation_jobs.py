import pytest
from unittest.mock import patch, MagicMock
from chalkbio.jobs.daily import run_validations

# We test the helper function directly, as testing the Celery task itself is more complex.
# This ensures the core logic (like alerting) works as expected.

@patch('requests.post')
def test_post_to_slack_on_failure(mock_post):
    """
    Ensure the slack notification function is called with the correct payload.
    """
    job_name = "test_job"
    error_message = "Something went wrong"
    
    # We need to mock the settings object
    with patch('chalkbio.jobs.daily.run_validations.settings') as mock_settings:
        mock_settings.SLACK_WEBHOOK_URL = "https://fake.slack.url/hook"
        
        run_validations.post_to_slack(job_name=job_name, error_message=error_message)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['text'] == f":x: Job Failed: *{job_name}*\n*Error*: {error_message}"

@patch('requests.post')
def test_post_to_slack_skipped_if_no_url(mock_post):
    """
    Ensure no request is made if the Slack webhook URL is not configured.
    """
    with patch('chalkbio.jobs.daily.run_validations.settings') as mock_settings:
        mock_settings.SLACK_WEBHOOK_URL = None
        
        run_validations.post_to_slack(job_name="test", error_message="test_error")

        mock_post.assert_not_called()
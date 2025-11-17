import pytest
from unittest.mock import patch

from tests.conftest import client
def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ChalkBio API"}
def test_get_top_investigators(client):
    """Test the top investigators endpoint."""
    response = client.get("/api/investigators/top?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
@patch("chalkbio.models.predict.get_prediction_for_trial")
def test_predict_trial_success(mock_get_prediction, client):
    """Test the prediction endpoint with a mocked prediction function."""
    trial_id = "NCT123456"
    mock_response = {
    "trial_id": trial_id,
    "drug_id": "DRUG-XYZ",
    "predicted_probability": 0.68,
    "confidence_lower": 0.56,
    "confidence_upper": 0.80,
    "model_version": "v1.0",
    "created_at": "2025-11-17T15:00:00Z"
    }
    mock_get_prediction.return_value = mock_response

    response = client.get(f"/api/predictions/trial/{trial_id}")

    assert response.status_code == 200
    assert response.json()["trial_id"] == trial_id
    assert response.json()["predicted_probability"] == 0.68
    mock_get_prediction.assert_called_once()

@patch("chalkbio.models.predict.get_prediction_for_trial")
def test_predict_trial_not_found(mock_get_prediction, client):
    """Test the prediction endpoint for a trial that doesn't exist."""
    mock_get_prediction.return_value = None
    trial_id = "NCT_NOT_FOUND"

    response = client.get(f"/api/predictions/trial/{trial_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"No prediction available for trial ID: {trial_id}"
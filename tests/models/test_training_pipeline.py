import os
import pytest
from chalkbio.models import train

def test_training_pipeline_creates_artifact(tmp_path):
    """
    Tests if the training pipeline runs and creates a model artifact file.
    Uses pytest's built-in `tmp_path` fixture to create a temporary directory.
    """
    # Override the default artifact directory to use the temporary one
    original_path = train.MODEL_ARTIFACT_DIR
    train.MODEL_ARTIFACT_DIR = tmp_path
    train.MODEL_ARTIFACT_PATH = f"{tmp_path}/{train.MODEL_NAME}_{train.MODEL_VERSION}.pkl"

    # Run the training pipeline
    train.run_training_pipeline()

    # Check if the model file was created
    assert os.path.exists(train.MODEL_ARTIFACT_PATH)
    assert os.path.getsize(train.MODEL_ARTIFACT_PATH) > 0

    # Clean up by restoring the original path for other tests
    train.MODEL_ARTIFACT_DIR = original_path
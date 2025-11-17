import pytest
from fastapi.testclient import TestClient
from chalkbio.main import app

@pytest.fixture(scope="module")
def client():
    """
    Yield a TestClient for the API.
    """
    with TestClient(app) as c:
        yield c
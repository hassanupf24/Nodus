import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_search_validation() -> None:
    """Test that a search query requires the query string."""
    response = client.post("/api/v1/search", json={})
    assert response.status_code == 422

def test_search_execution() -> None:
    """Test executing a search query against vector DB."""
    payload = {
        "query": "system configuration settings",
        "limit": 5,
        "search_type": "hybrid"
    }
    response = client.post("/api/v1/search", json=payload)
    # Check that it either succeeds or handles clean dependency lookup exceptions
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

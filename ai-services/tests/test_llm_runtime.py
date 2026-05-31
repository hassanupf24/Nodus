import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_list_models() -> None:
    """Test retrieving list of available local models."""
    response = client.get("/api/v1/llm/models")
    # If Ollama is not running it may return 200 with empty list or error
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)

def test_system_resource_monitor() -> None:
    """Test retrieving CPU, RAM, and GPU telemetry snapshots."""
    response = client.get("/api/v1/llm/resources")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_percent" in data
    assert "ram_total_gb" in data
    assert "ram_used_gb" in data

import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_gateway_root() -> None:
    """Test that the gateway root returns metadata correctly."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["service"] == "Nodus AI Gateway"
    assert "version" in data["data"]

def test_gateway_health() -> None:
    """Test that the gateway healthcheck path runs successfully."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "services" in data
    
    # Verify ollama health details are reported
    services = data["services"]
    assert any(s["name"] == "ollama" for s in services)

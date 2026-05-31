import pytest
from fastapi.testclient import TestClient
from vector_services.router import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_create_collection() -> None:
    """Test creating a vector collection."""
    payload = {
        "name": "test_collection",
        "vector_size": 384,
        "distance_metric": "Cosine"
    }
    response = client.post("/vector/collections", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_upsert_and_search() -> None:
    """Test upserting vector points and running a vector query."""
    # Ensure collection is created
    client.post("/vector/collections", json={"name": "test_collection", "vector_size": 3})

    upsert_payload = {
        "points": [
            {
                "id": 1,
                "vector": [0.1, 0.2, 0.3],
                "payload": {"text": "matching chunk", "source": "test.txt"}
            }
        ]
    }
    response = client.post("/vector/collections/test_collection/upsert", json=upsert_payload)
    assert response.status_code == 200
    assert response.json()["count"] == 1

    search_payload = {
        "vector": [0.1, 0.2, 0.3],
        "limit": 1
    }
    response = client.post("/vector/collections/test_collection/search", json=search_payload)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["id"] == "1"

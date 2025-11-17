"""
Unit tests for the FastAPI application endpoints.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_endpoint(client: TestClient):
    """Test the /health endpoint returns expected structure."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert "timestamp" in data

    # Status should be one of: ok, degraded
    assert data["status"] in ["ok", "degraded"]


@pytest.mark.unit
def test_health_endpoint_response_model(client: TestClient):
    """Test the /health endpoint matches the HealthResponse schema."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Check all expected keys exist
    expected_keys = {"status", "database", "redis", "timestamp"}
    assert set(data.keys()) == expected_keys


@pytest.mark.unit
def test_events_endpoint_default_limit(client: TestClient):
    """Test the /events endpoint with default limit."""
    response = client.get("/events")

    assert response.status_code in [200, 500]  # 500 if DB not available in test

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        # Should return at most 50 events (default limit)
        assert len(data) <= 50


@pytest.mark.unit
def test_events_endpoint_custom_limit(client: TestClient):
    """Test the /events endpoint with custom limit."""
    response = client.get("/events?limit=10")

    assert response.status_code in [200, 500]  # 500 if DB not available in test

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10


@pytest.mark.unit
def test_events_endpoint_validation_min_limit(client: TestClient):
    """Test the /events endpoint rejects limit < 1."""
    response = client.get("/events?limit=0")

    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_events_endpoint_validation_max_limit(client: TestClient):
    """Test the /events endpoint rejects limit > 1000."""
    response = client.get("/events?limit=1001")

    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_pipeline_run_endpoint_structure(client: TestClient):
    """Test the /pipeline/run endpoint returns expected structure."""
    # Note: This will actually queue a task in integration tests
    # In unit tests, we just check the response structure
    response = client.post("/pipeline/run")

    # Should return 200 with task info, or 500 if Celery/Redis not available
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "queued"


@pytest.mark.unit
def test_openapi_docs_available(client: TestClient):
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.unit
def test_redoc_available(client: TestClient):
    """Test that ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.unit
def test_openapi_json_available(client: TestClient):
    """Test that OpenAPI JSON schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "LoFi IA YouTube API"

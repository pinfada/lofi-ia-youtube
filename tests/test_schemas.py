"""
Unit tests for Pydantic schemas.
"""
import pytest
from datetime import datetime


@pytest.mark.unit
def test_health_response_schema():
    """Test HealthResponse schema validation."""
    from schemas import HealthResponse

    data = {
        "status": "ok",
        "database": "ok",
        "redis": "ok",
        "timestamp": datetime.utcnow()
    }

    response = HealthResponse(**data)
    assert response.status == "ok"
    assert response.database == "ok"
    assert response.redis == "ok"


@pytest.mark.unit
def test_pipeline_run_response_schema():
    """Test PipelineRunResponse schema validation."""
    from schemas import PipelineRunResponse

    data = {
        "task_id": "abc-123-def",
        "status": "queued"
    }

    response = PipelineRunResponse(**data)
    assert response.task_id == "abc-123-def"
    assert response.status == "queued"


@pytest.mark.unit
def test_event_response_schema():
    """Test EventResponse schema validation."""
    from schemas import EventResponse

    data = {
        "id": 123,
        "created_at": datetime.utcnow(),
        "kind": "pipeline",
        "status": "ok"
    }

    response = EventResponse(**data)
    assert response.id == 123
    assert response.kind == "pipeline"


@pytest.mark.unit
def test_video_create_request_validation():
    """Test VideoCreateRequest validation."""
    from schemas import VideoCreateRequest

    # Valid data
    data = {
        "title": "Test Video",
        "description": "A test video",
        "tags": ["lofi", "test"],
        "duration_sec": 3600
    }

    request = VideoCreateRequest(**data)
    assert request.title == "Test Video"
    assert len(request.tags) == 2


@pytest.mark.unit
def test_video_create_request_validation_title_required():
    """Test VideoCreateRequest requires title."""
    from schemas import VideoCreateRequest
    from pydantic import ValidationError

    # Missing title
    with pytest.raises(ValidationError):
        VideoCreateRequest(description="Test", tags=[])


@pytest.mark.unit
def test_video_create_request_validation_title_min_length():
    """Test VideoCreateRequest title minimum length."""
    from schemas import VideoCreateRequest
    from pydantic import ValidationError

    # Empty title
    with pytest.raises(ValidationError):
        VideoCreateRequest(title="", description="Test")


@pytest.mark.unit
def test_video_response_schema():
    """Test VideoResponse schema validation."""
    from schemas import VideoResponse

    data = {
        "id": 456,
        "created_at": datetime.utcnow(),
        "title": "Test Video",
        "description": "A test video",
        "tags": ["lofi", "test"],
        "duration_sec": 3600,
        "file_path": "/data/video.mp4",
        "youtube_video_id": "abc123",
        "status": "uploaded"
    }

    response = VideoResponse(**data)
    assert response.id == 456
    assert response.title == "Test Video"
    assert response.youtube_video_id == "abc123"


@pytest.mark.unit
def test_error_response_schema():
    """Test ErrorResponse schema validation."""
    from schemas import ErrorResponse

    data = {
        "detail": "An error occurred",
        "error_code": "ERR_001"
    }

    response = ErrorResponse(**data)
    assert response.detail == "An error occurred"
    assert response.error_code == "ERR_001"
    assert response.timestamp is not None

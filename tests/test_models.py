"""
Unit tests for SQLAlchemy ORM models.
"""
import pytest
from datetime import datetime


@pytest.mark.unit
def test_event_model_imports():
    """Test that Event model can be imported."""
    from models import Event
    assert Event is not None


@pytest.mark.unit
def test_video_model_imports():
    """Test that Video model can be imported."""
    from models import Video
    assert Video is not None


@pytest.mark.unit
def test_event_model_attributes():
    """Test that Event model has expected attributes."""
    from models import Event

    # Check table name
    assert Event.__tablename__ == "events"

    # Check columns exist
    assert hasattr(Event, "id")
    assert hasattr(Event, "created_at")
    assert hasattr(Event, "kind")
    assert hasattr(Event, "status")
    assert hasattr(Event, "payload")


@pytest.mark.unit
def test_video_model_attributes():
    """Test that Video model has expected attributes."""
    from models import Video

    # Check table name
    assert Video.__tablename__ == "videos"

    # Check columns exist
    assert hasattr(Video, "id")
    assert hasattr(Video, "created_at")
    assert hasattr(Video, "title")
    assert hasattr(Video, "description")
    assert hasattr(Video, "tags")
    assert hasattr(Video, "duration_sec")
    assert hasattr(Video, "file_path")
    assert hasattr(Video, "youtube_video_id")
    assert hasattr(Video, "status")


@pytest.mark.unit
def test_event_model_repr():
    """Test Event model __repr__ method."""
    from models import Event

    # Create a mock event (not persisted to DB)
    event = Event()
    event.id = 123
    event.kind = "test"
    event.status = "ok"

    repr_str = repr(event)
    assert "Event" in repr_str
    assert "123" in repr_str
    assert "test" in repr_str


@pytest.mark.unit
def test_video_model_repr():
    """Test Video model __repr__ method."""
    from models import Video

    # Create a mock video (not persisted to DB)
    video = Video()
    video.id = 456
    video.title = "Test Video"
    video.youtube_video_id = "abc123"

    repr_str = repr(video)
    assert "Video" in repr_str
    assert "456" in repr_str
    assert "Test Video" in repr_str

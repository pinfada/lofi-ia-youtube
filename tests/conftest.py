"""
Pytest configuration and fixtures for LoFi IA YouTube tests.
"""
import sys
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add api directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from app import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client.

    Yields:
        TestClient instance for making API requests
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_event_data():
    """
    Provide sample event data for testing.

    Returns:
        Dictionary with sample event data
    """
    return {
        "kind": "test_event",
        "status": "ok",
        "payload": {"test_key": "test_value", "count": 42}
    }


@pytest.fixture
def sample_video_data():
    """
    Provide sample video data for testing.

    Returns:
        Dictionary with sample video data
    """
    return {
        "title": "Test Lo-Fi Video",
        "description": "A test video for unit testing",
        "tags": ["lofi", "test", "music"],
        "duration_sec": 3600
    }

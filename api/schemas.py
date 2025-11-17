"""
Pydantic schemas for request/response validation and API documentation.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Overall health status")
    database: str = Field(..., description="Database connection status")
    redis: str = Field(..., description="Redis connection status")
    timestamp: datetime = Field(..., description="Current server timestamp")


class PipelineRunResponse(BaseModel):
    """Response model for pipeline run endpoint."""
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status (queued, running, completed, failed)")


class EventResponse(BaseModel):
    """Response model for event records."""
    id: int = Field(..., description="Event ID")
    created_at: datetime = Field(..., description="Event creation timestamp")
    kind: str = Field(..., description="Event type")
    status: str = Field(..., description="Event status")

    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    """Detailed response model for event records including payload."""
    payload: Dict[str, Any] = Field(..., description="Event payload data")


class VideoCreateRequest(BaseModel):
    """Request model for creating a video record."""
    title: str = Field(..., min_length=1, max_length=100, description="Video title")
    description: Optional[str] = Field(None, max_length=5000, description="Video description")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    duration_sec: Optional[int] = Field(None, gt=0, description="Video duration in seconds")


class VideoResponse(BaseModel):
    """Response model for video records."""
    id: int = Field(..., description="Video ID")
    created_at: datetime = Field(..., description="Video creation timestamp")
    title: Optional[str] = Field(None, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    tags: Optional[List[str]] = Field(None, description="Video tags")
    duration_sec: Optional[int] = Field(None, description="Video duration in seconds")
    file_path: Optional[str] = Field(None, description="Local file path")
    youtube_video_id: Optional[str] = Field(None, description="YouTube video ID")
    status: str = Field(..., description="Video status")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

"""
SQLAlchemy ORM models for the LoFi IA YouTube application.
"""
from sqlalchemy import Column, BigInteger, Text, Integer, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Event(Base):
    """
    Event model for tracking pipeline execution and system events.

    Attributes:
        id: Primary key
        created_at: Timestamp of event creation
        kind: Type of event (e.g., 'pipeline', 'upload', 'error')
        status: Event status ('ok', 'error', 'pending')
        payload: JSON data containing event details
    """
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    kind = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default='ok')
    payload = Column(JSONB, nullable=False)

    def __repr__(self):
        return f"<Event(id={self.id}, kind='{self.kind}', status='{self.status}')>"


class Video(Base):
    """
    Video model for storing metadata about generated and uploaded videos.

    Attributes:
        id: Primary key
        created_at: Timestamp of video creation
        title: Video title
        description: Video description
        tags: Array of tags
        duration_sec: Video duration in seconds
        file_path: Local file path to the video
        youtube_video_id: YouTube video ID after upload
        status: Video status ('pending', 'uploaded', 'error')
    """
    __tablename__ = "videos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    title = Column(Text)
    description = Column(Text)
    tags = Column(ARRAY(Text))
    duration_sec = Column(Integer)
    file_path = Column(Text)
    youtube_video_id = Column(Text)
    status = Column(Text, nullable=False, default='pending')

    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', youtube_id='{self.youtube_video_id}')>"

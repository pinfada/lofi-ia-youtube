"""
Configuration management with Pydantic validation.

This module provides a validated configuration system using Pydantic BaseSettings.
All environment variables are validated at startup with clear error messages.
"""
import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated using Pydantic. Missing or invalid values
    will raise validation errors with clear messages.
    """

    # API Keys
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for image generation"
    )
    stability_api_key: Optional[str] = Field(
        default=None,
        description="Stability AI API key for image generation"
    )
    pika_api_key: Optional[str] = Field(
        default=None,
        description="Pika API key for video animation"
    )
    mubert_api_key: Optional[str] = Field(
        default=None,
        description="Mubert API key for music generation"
    )

    # YouTube credentials
    youtube_client_id: Optional[str] = Field(
        default=None,
        description="YouTube OAuth client ID"
    )
    youtube_client_secret: Optional[str] = Field(
        default=None,
        description="YouTube OAuth client secret"
    )
    youtube_refresh_token: Optional[str] = Field(
        default=None,
        description="YouTube OAuth refresh token"
    )

    # Database & Redis
    database_url: str = Field(
        default="postgresql+psycopg2://lofi:lofi@db:5432/lofi",
        description="PostgreSQL database URL"
    )
    redis_url: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL"
    )

    # Storage paths
    media_root: str = Field(
        default="/data",
        description="Root directory for media files"
    )
    audio_dir: str = Field(
        default="/data/MP3_NORMALIZED",
        description="Directory containing audio files"
    )
    loop_video: str = Field(
        default="/data/loop_seamless.mp4",
        description="Path to seamless video loop"
    )
    intro_video: str = Field(
        default="/app/static/intro.mp4",
        description="Path to intro video"
    )
    outro_video: str = Field(
        default="/app/static/outro.mp4",
        description="Path to outro video"
    )

    # Default video metadata
    default_title: str = Field(
        default="Lo-Fi Midnight Café — Beats to Study, Chill & Sleep",
        description="Default video title"
    )
    default_description: str = Field(
        default="Chill beats for studying, relaxing or sleeping. New mixes regularly.",
        description="Default video description"
    )
    default_tags: str = Field(
        default="lofi,study beats,relax,chill,focus,deep work",
        description="Comma-separated list of default tags"
    )

    # API settings
    api_host: str = Field(
        default="0.0.0.0",
        description="API host address"
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API port number"
    )
    api_workers: int = Field(
        default=1,
        ge=1,
        description="Number of API workers"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60,
        ge=1,
        description="Maximum requests per minute per IP"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Environment name (development, staging, production)"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is valid."""
        valid_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of: {', '.join(valid_envs)}")
        return v_lower

    def get_tags_list(self) -> List[str]:
        """
        Get tags as a list.

        Returns:
            List of tags
        """
        return [tag.strip() for tag in self.default_tags.split(",") if tag.strip()]

    def is_production(self) -> bool:
        """
        Check if running in production environment.

        Returns:
            True if production, False otherwise
        """
        return self.environment == "production"

    def is_development(self) -> bool:
        """
        Check if running in development environment.

        Returns:
            True if development, False otherwise
        """
        return self.environment == "development"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Map environment variables to field names
        env_prefix = ""


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings instance
    """
    return settings

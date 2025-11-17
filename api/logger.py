"""
Structured logging configuration for the application.
"""
import logging
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Format as simple key=value pairs for readability
        return " ".join(f"{k}={v}" for k, v in log_data.items())


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a structured logger with JSON formatting.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Log a message with additional context fields.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context fields
    """
    log_method = getattr(logger, level.lower())
    extra = {"extra_fields": kwargs}
    log_method(message, extra=extra)


# Default application logger
app_logger = setup_logger("lofi_ia_youtube")

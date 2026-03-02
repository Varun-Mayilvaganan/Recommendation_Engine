"""Centralized structured logging configuration.

All controllers and services must use this logger. No random hardcoded log messages.
"""

import logging
import sys
from typing import Any

# Log format: timestamp | level | module | message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _configure_logger(name: str) -> logging.Logger:
    """Create and configure a named logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = _configure_logger("app")


def log_api_entry(endpoint: str, method: str, **kwargs: Any) -> None:
    """Log API request entry."""
    extra = " | ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
    logger.info("API_ENTRY | %s %s | %s", method, endpoint, extra or "—")


def log_api_success(endpoint: str, message: str = "Success") -> None:
    """Log API success response."""
    logger.info("API_SUCCESS | %s | %s", endpoint, message)


def log_api_error(endpoint: str, error: str, error_code: str | None = None) -> None:
    """Log API error."""
    logger.error(
        "API_ERROR | %s | error=%s | error_code=%s",
        endpoint,
        error,
        error_code or "—",
    )

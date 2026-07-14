"""
StudyMate AI — Structured Logging Module.

Provides a centralized logging configuration with structured output,
correlation IDs for request tracing, and colored console output.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional


# Context variable for request correlation
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class StructuredFormatter(logging.Formatter):
    """Custom formatter that produces structured, readable log output."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True) -> None:
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with timestamp, level, correlation ID, and message."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level = record.levelname
        correlation_id = correlation_id_var.get("")
        module = record.module
        message = record.getMessage()

        # Build correlation segment
        corr_segment = f" [{correlation_id}]" if correlation_id else ""

        if self.use_colors:
            color = self.COLORS.get(level, "")
            formatted = (
                f"{self.RESET}{timestamp} "
                f"{color}{level:<8}{self.RESET}"
                f"{corr_segment} "
                f"[{module}] {message}"
            )
        else:
            formatted = (
                f"{timestamp} {level:<8}{corr_segment} [{module}] {message}"
            )

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(level: str = "INFO") -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    root_logger = logging.getLogger("studymate")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter(use_colors=True))
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    for noisy_logger in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger under the 'studymate' namespace.

    Args:
        name: Logger name (typically the module name).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"studymate.{name}")


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return uuid.uuid4().hex[:12]


def set_correlation_id(cid: Optional[str] = None) -> str:
    """
    Set the correlation ID for the current context.

    Args:
        cid: Optional correlation ID. Generates one if not provided.

    Returns:
        The active correlation ID.
    """
    if cid is None:
        cid = generate_correlation_id()
    correlation_id_var.set(cid)
    return cid

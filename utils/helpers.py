"""
StudyMate AI — General Utility Functions.

Provides common helper functions used across modules:
UUID generation, timestamp formatting, JSON parsing, and text utilities.
"""

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


def generate_id() -> str:
    """Generate a unique ID string (UUID4 hex)."""
    return uuid.uuid4().hex


def utc_now() -> str:
    """Return current UTC timestamp as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def utc_now_datetime() -> datetime:
    """Return current UTC datetime object."""
    return datetime.now(timezone.utc)


def safe_json_parse(text: str) -> Optional[dict[str, Any]]:
    """
    Attempt to parse a JSON string, handling common LLM output issues.

    Tries direct parsing first, then attempts to extract JSON from
    markdown code blocks or surrounding text.

    Args:
        text: Raw string that may contain JSON.

    Returns:
        Parsed dictionary, or None if parsing fails.
    """
    # Direct parse attempt
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting from markdown code blocks
    code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding JSON object in the text
    brace_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    match = re.search(brace_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, preserving word boundaries.

    Args:
        text: Input text to truncate.
        max_length: Maximum character length.
        suffix: Suffix to append when truncated.

    Returns:
        Truncated text with suffix if needed.
    """
    if len(text) <= max_length:
        return text

    truncated = text[: max_length - len(suffix)]
    # Try to break at a word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.5:
        truncated = truncated[:last_space]

    return truncated + suffix


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by stripping dangerous characters.

    Args:
        text: Raw user input.

    Returns:
        Sanitized text safe for processing.
    """
    # Remove null bytes and control characters (except newlines/tabs)
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return sanitized.strip()


def format_duration(minutes: int) -> str:
    """
    Format a duration in minutes to a human-readable string.

    Args:
        minutes: Duration in minutes.

    Returns:
        Formatted string like '2h 30m' or '45m'.
    """
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"

    return f"{hours}h {remaining_minutes}m"


def calculate_percentage(part: float, total: float) -> float:
    """
    Calculate percentage safely, avoiding division by zero.

    Args:
        part: The numerator value.
        total: The denominator value.

    Returns:
        Percentage as a float (0.0 to 100.0).
    """
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 1)

"""
StudyMate AI — Retry Decorator Module.

Provides configurable retry logic with exponential backoff
for LLM calls, MCP tool invocations, and database operations.
"""

import asyncio
import functools
from typing import Any, Callable, Optional, Sequence, Type

from utils.logger import get_logger

logger = get_logger("retry")


class MaxRetriesExceededError(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"Max retries ({attempts}) exceeded. Last error: {last_error}"
        )


def retry_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
) -> Callable:
    """
    Async retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including the first try).
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Maximum delay cap in seconds.
        backoff_factor: Multiplier applied to delay after each retry.
        retryable_exceptions: Tuple of exception types that trigger a retry.
        on_retry: Optional callback invoked on each retry with (attempt, error).

    Returns:
        Decorated async function with retry behavior.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            delay = base_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except tuple(retryable_exceptions) as exc:
                    last_exception = exc

                    if attempt == max_attempts:
                        logger.error(
                            "All %d attempts failed for %s: %s",
                            max_attempts,
                            func.__name__,
                            exc,
                        )
                        raise MaxRetriesExceededError(max_attempts, exc) from exc

                    logger.warning(
                        "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                        attempt,
                        max_attempts,
                        func.__name__,
                        exc,
                        delay,
                    )

                    if on_retry:
                        on_retry(attempt, exc)

                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            # Should never reach here, but satisfies type checker
            raise MaxRetriesExceededError(max_attempts, last_exception)  # type: ignore

        return wrapper

    return decorator


def retry_sync(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
) -> Callable:
    """
    Synchronous retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay cap in seconds.
        backoff_factor: Multiplier for delay growth.
        retryable_exceptions: Exception types that trigger retry.

    Returns:
        Decorated sync function with retry behavior.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import time

            last_exception: Optional[Exception] = None
            delay = base_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(retryable_exceptions) as exc:
                    last_exception = exc

                    if attempt == max_attempts:
                        raise MaxRetriesExceededError(max_attempts, exc) from exc

                    logger.warning(
                        "Sync attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                        attempt,
                        max_attempts,
                        func.__name__,
                        exc,
                        delay,
                    )

                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            raise MaxRetriesExceededError(max_attempts, last_exception)  # type: ignore

        return wrapper

    return decorator

"""Retry utilities with exponential back-off and jitter.

Example:
    >>> @retry(max_attempts=3, exceptions=(IOError,))
    ... async def fetch():
    ...     ...
"""

from __future__ import annotations

import asyncio
import functools
import logging
import random
from typing import Any, Callable, Tuple, Type, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    *,
    max_attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> Callable[[F], F]:
    """Async decorator that retries the wrapped coroutine on failure.

    Args:
        max_attempts: Maximum number of call attempts (including the first).
        exceptions: Tuple of exception types to catch and retry on.
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Maximum delay cap in seconds.
        exponential_base: Base for exponential back-off calculation.
        jitter: When ``True``, adds random jitter to the delay.

    Returns:
        A decorator that wraps an async function with retry logic.

    Example:
        >>> @retry(max_attempts=5, exceptions=(ConnectionError,))
        ... async def call_external_api():
        ...     ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.error(
                            "Max retry attempts reached",
                            extra={
                                "function": func.__qualname__,
                                "attempt": attempt,
                                "error": str(exc),
                            },
                        )
                        raise
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    if jitter:
                        delay *= 0.5 + random.random() * 0.5
                    logger.warning(
                        "Retrying after error",
                        extra={
                            "function": func.__qualname__,
                            "attempt": attempt,
                            "delay_s": round(delay, 3),
                            "error": str(exc),
                        },
                    )
                    await asyncio.sleep(delay)
            raise RuntimeError("Unreachable") from last_exc  # pragma: no cover

        return wrapper  # type: ignore[return-value]

    return decorator


async def retry_call(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    **kwargs: Any,
) -> Any:
    """Call an async function with retry logic without using a decorator.

    Args:
        func: The async callable to call.
        *args: Positional arguments forwarded to ``func``.
        max_attempts: Maximum number of attempts.
        exceptions: Exception types to catch.
        base_delay: Base retry delay in seconds.
        max_delay: Maximum retry delay cap.
        **kwargs: Keyword arguments forwarded to ``func``.

    Returns:
        The return value of ``func`` on success.

    Raises:
        The last exception if all attempts are exhausted.
    """
    decorated = retry(
        max_attempts=max_attempts,
        exceptions=exceptions,
        base_delay=base_delay,
        max_delay=max_delay,
    )(func)
    return await decorated(*args, **kwargs)

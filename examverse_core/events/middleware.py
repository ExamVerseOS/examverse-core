"""Event middleware pipeline for the ExamVerse event bus.

Middleware wraps event dispatch to add cross-cutting concerns such as
structured logging, metrics, retry budgeting, and correlation injection.

Example:
    >>> class LoggingMiddleware(EventMiddleware):
    ...     async def __call__(self, event, call_next):
    ...         print(f"Publishing {event.event_type}")
    ...         await call_next(event)
"""

from __future__ import annotations

import abc
import logging
import time
from typing import Awaitable, Callable

from examverse_core.events.base import DomainEvent

logger = logging.getLogger(__name__)

Next = Callable[[DomainEvent], Awaitable[None]]


class EventMiddleware(abc.ABC):
    """Abstract base for event bus middleware.

    Middleware is called in registration order before event handlers are
    invoked. Each implementation must call ``await call_next(event)`` to
    continue the chain.
    """

    @abc.abstractmethod
    async def __call__(self, event: DomainEvent, call_next: Next) -> None:
        """Process the event and optionally delegate to the next middleware.

        Args:
            event: The domain event being published.
            call_next: Async callable that invokes the next middleware or handlers.
        """


class LoggingMiddleware(EventMiddleware):
    """Logs every event publication with timing information.

    Emits a structured log entry at DEBUG level before dispatch and at INFO
    level after, including the event type, event ID, and elapsed milliseconds.
    """

    async def __call__(self, event: DomainEvent, call_next: Next) -> None:
        """Log the event and pass it along the middleware chain.

        Args:
            event: The domain event being published.
            call_next: Next middleware or handler invoker.
        """
        start = time.perf_counter()
        logger.debug(
            "Publishing event",
            extra={
                "event_type": event.event_type,
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
            },
        )
        await call_next(event)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Event published",
            extra={
                "event_type": event.event_type,
                "event_id": event.event_id,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )


class CorrelationMiddleware(EventMiddleware):
    """Propagates correlation IDs from a context variable into each event.

    When a correlation ID is present in the logging context, this middleware
    copies it into ``event.correlation_id`` so all handlers receive a
    traceable event.
    """

    async def __call__(self, event: DomainEvent, call_next: Next) -> None:
        """Inject correlation ID from context and delegate.

        Args:
            event: The domain event being published.
            call_next: Next middleware or handler invoker.
        """
        from examverse_core.logging.context import get_correlation_id

        if event.correlation_id is None:
            correlation_id = get_correlation_id()
            if correlation_id:
                object.__setattr__(event, "correlation_id", correlation_id)
        await call_next(event)

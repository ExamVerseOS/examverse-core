"""Logging context — correlation and trace IDs for distributed tracing.

Context variables propagate IDs through async call chains without requiring
explicit parameter threading. All log entries produced via
:func:`~examverse_core.logging.logger.get_logger` automatically include
these IDs.

Example:
    >>> set_correlation_id("req-abc-123")
    >>> get_correlation_id()
    'req-abc-123'
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str | None] = ContextVar("_correlation_id", default=None)
_trace_id: ContextVar[str | None] = ContextVar("_trace_id", default=None)
_span_id: ContextVar[str | None] = ContextVar("_span_id", default=None)
_request_id: ContextVar[str | None] = ContextVar("_request_id", default=None)


def set_correlation_id(value: str | None = None) -> str:
    """Set the active correlation ID for the current async context.

    Args:
        value: The correlation ID to set. A new UUID v4 is generated when
            ``None`` is passed.

    Returns:
        The correlation ID that was set.
    """
    id_ = value or str(uuid.uuid4())
    _correlation_id.set(id_)
    return id_


def get_correlation_id() -> str | None:
    """Retrieve the active correlation ID.

    Returns:
        The correlation ID, or ``None`` if not set.
    """
    return _correlation_id.get()


def set_trace_id(value: str | None = None) -> str:
    """Set the active trace ID for the current async context.

    Args:
        value: The trace ID to set. A new UUID v4 is generated when omitted.

    Returns:
        The trace ID that was set.
    """
    id_ = value or str(uuid.uuid4())
    _trace_id.set(id_)
    return id_


def get_trace_id() -> str | None:
    """Retrieve the active trace ID.

    Returns:
        The trace ID, or ``None`` if not set.
    """
    return _trace_id.get()


def set_span_id(value: str | None = None) -> str:
    """Set the active span ID for the current async context.

    Args:
        value: The span ID to set. A new UUID v4 is generated when omitted.

    Returns:
        The span ID that was set.
    """
    id_ = value or str(uuid.uuid4())
    _span_id.set(id_)
    return id_


def get_span_id() -> str | None:
    """Retrieve the active span ID.

    Returns:
        The span ID, or ``None`` if not set.
    """
    return _span_id.get()


def set_request_id(value: str | None = None) -> str:
    """Set the active request ID for the current async context.

    Args:
        value: The request ID to set. A new UUID v4 is generated when omitted.

    Returns:
        The request ID that was set.
    """
    id_ = value or str(uuid.uuid4())
    _request_id.set(id_)
    return id_


def get_request_id() -> str | None:
    """Retrieve the active request ID.

    Returns:
        The request ID, or ``None`` if not set.
    """
    return _request_id.get()


def clear_context() -> None:
    """Reset all context variables to ``None`` in the current async context."""
    _correlation_id.set(None)
    _trace_id.set(None)
    _span_id.set(None)
    _request_id.set(None)


def get_log_context() -> dict[str, str | None]:
    """Return all active context IDs as a dict suitable for log ``extra``.

    Returns:
        Dict with keys ``correlation_id``, ``trace_id``, ``span_id``,
        ``request_id`` mapped to their current values.
    """
    return {
        "correlation_id": get_correlation_id(),
        "trace_id": get_trace_id(),
        "span_id": get_span_id(),
        "request_id": get_request_id(),
    }

"""Structured JSON logging for the ExamVerseOS ecosystem.

Configures structlog with a JSON renderer and automatic context injection
(correlation IDs, trace IDs, service name, environment). All application code
should obtain loggers via :func:`get_logger` rather than using the stdlib
``logging`` module directly.

Example:
    >>> from examverse_core.logging import configure_logging, get_logger
    >>> configure_logging(service_name="examverse-api", log_level="INFO")
    >>> log = get_logger(__name__)
    >>> log.info("Request received", path="/api/exams", method="GET")
"""

from __future__ import annotations

import logging
import logging.config
import sys
from typing import Any

import structlog

from examverse_core.logging.context import get_log_context

_configured: bool = False


def _add_service_context(
    logger: Any, method: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Structlog processor that injects the log context IDs.

    Args:
        logger: The bound structlog logger.
        method: The log method name.
        event_dict: The current event dictionary.

    Returns:
        The event dict with context IDs merged in.
    """
    ctx = get_log_context()
    for key, value in ctx.items():
        if value is not None:
            event_dict.setdefault(key, value)
    return event_dict


def configure_logging(
    *,
    service_name: str = "examverse",
    log_level: str = "INFO",
    json_output: bool = True,
    environment: str = "development",
) -> None:
    """Configure structlog for the current process.

    Should be called once at application startup before any log statements
    are emitted. Subsequent calls are no-ops.

    Args:
        service_name: The service name embedded in every log record.
        log_level: Root log level (``DEBUG``, ``INFO``, ``WARNING``, etc.).
        json_output: When ``True``, emit newline-delimited JSON. When
            ``False``, use a coloured human-readable format.
        environment: The active deployment environment.
    """
    global _configured
    if _configured:
        return

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_service_context,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_output:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(numeric_level)

    structlog.contextvars.bind_contextvars(
        service=service_name,
        environment=environment,
    )

    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger for the given module name.

    Args:
        name: Logger name; typically ``__name__`` of the calling module.
            Defaults to the root logger.

    Returns:
        A :class:`structlog.stdlib.BoundLogger` instance.

    Example:
        >>> log = get_logger(__name__)
        >>> log.info("hello", user_id="u123")
    """
    return structlog.get_logger(name)


def reset_logging() -> None:
    """Reset the logging configuration flag.

    Intended for use in tests that need a fresh logging setup between runs.
    """
    global _configured
    _configured = False

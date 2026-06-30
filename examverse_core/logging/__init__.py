"""ExamVerse structured logging — JSON output with correlation ID injection."""

from examverse_core.logging.context import (
    clear_context,
    get_correlation_id,
    get_log_context,
    get_request_id,
    get_span_id,
    get_trace_id,
    set_correlation_id,
    set_request_id,
    set_span_id,
    set_trace_id,
)
from examverse_core.logging.logger import configure_logging, get_logger, reset_logging

__all__ = [
    "configure_logging",
    "get_logger",
    "reset_logging",
    "set_correlation_id",
    "get_correlation_id",
    "set_trace_id",
    "get_trace_id",
    "set_span_id",
    "get_span_id",
    "set_request_id",
    "get_request_id",
    "get_log_context",
    "clear_context",
]

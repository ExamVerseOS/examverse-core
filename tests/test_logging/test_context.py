"""Tests for logging context variable utilities."""

from __future__ import annotations

from examverse_core.logging.context import (
    clear_context,
    get_correlation_id,
    get_log_context,
    get_request_id,
    get_trace_id,
    set_correlation_id,
    set_request_id,
    set_trace_id,
)


class TestCorrelationId:
    def test_set_and_get(self) -> None:
        set_correlation_id("corr-123")
        assert get_correlation_id() == "corr-123"

    def test_auto_generate(self) -> None:
        cid = set_correlation_id()
        assert len(cid) == 36

    def test_none_when_unset(self) -> None:
        clear_context()
        assert get_correlation_id() is None


class TestTraceId:
    def test_set_and_get(self) -> None:
        set_trace_id("trace-abc")
        assert get_trace_id() == "trace-abc"


class TestRequestId:
    def test_set_and_get(self) -> None:
        set_request_id("req-xyz")
        assert get_request_id() == "req-xyz"


class TestClearContext:
    def test_clears_all(self) -> None:
        set_correlation_id("c")
        set_trace_id("t")
        set_request_id("r")
        clear_context()
        assert get_correlation_id() is None
        assert get_trace_id() is None
        assert get_request_id() is None


class TestGetLogContext:
    def test_returns_dict(self) -> None:
        clear_context()
        set_correlation_id("c1")
        ctx = get_log_context()
        assert isinstance(ctx, dict)
        assert ctx["correlation_id"] == "c1"
        assert ctx["trace_id"] is None

"""Tests for retry decorator and retry_call."""

from __future__ import annotations

import pytest

from examverse_core.utils.retry import retry, retry_call


class TestRetryDecorator:
    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self) -> None:
        calls: list[int] = []

        @retry(max_attempts=3)
        async def fn() -> str:
            calls.append(1)
            return "ok"

        result = await fn()
        assert result == "ok"
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_retries_on_failure_then_succeeds(self) -> None:
        calls: list[int] = []

        @retry(max_attempts=3, base_delay=0.0, jitter=False)
        async def fn() -> str:
            calls.append(1)
            if len(calls) < 2:
                raise IOError("temporary")
            return "ok"

        result = await fn()
        assert result == "ok"
        assert len(calls) == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_attempts(self) -> None:
        @retry(max_attempts=3, base_delay=0.0, jitter=False, exceptions=(ValueError,))
        async def fn() -> None:
            raise ValueError("always fails")

        with pytest.raises(ValueError):
            await fn()

    @pytest.mark.asyncio
    async def test_does_not_catch_unspecified_exceptions(self) -> None:
        @retry(max_attempts=3, exceptions=(IOError,))
        async def fn() -> None:
            raise RuntimeError("not retried")

        with pytest.raises(RuntimeError):
            await fn()


class TestRetryCall:
    @pytest.mark.asyncio
    async def test_retry_call_succeeds(self) -> None:
        async def fn() -> str:
            return "hello"

        result = await retry_call(fn, max_attempts=2)
        assert result == "hello"

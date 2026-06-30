"""Tests for EventBus — publish/subscribe, middleware, priorities, and retries."""

from __future__ import annotations

import asyncio

import pytest

from examverse_core.events.base import DomainEvent
from examverse_core.events.bus import EventBus
from examverse_core.events.middleware import EventMiddleware, LoggingMiddleware


class UserCreated(DomainEvent):
    user_id: str


class OrderPlaced(DomainEvent):
    order_id: str


class TestSubscribeAndPublish:
    @pytest.mark.asyncio
    async def test_handler_called_on_publish(self) -> None:
        bus = EventBus()
        received: list[UserCreated] = []

        @bus.subscribe(UserCreated)
        async def handle(event: UserCreated) -> None:
            received.append(event)

        await bus.publish(UserCreated(user_id="u1"))
        assert len(received) == 1
        assert received[0].user_id == "u1"

    @pytest.mark.asyncio
    async def test_no_handler_does_not_raise(self) -> None:
        bus = EventBus()
        await bus.publish(OrderPlaced(order_id="o1"))

    @pytest.mark.asyncio
    async def test_multiple_handlers(self) -> None:
        bus = EventBus()
        calls: list[str] = []

        @bus.subscribe(UserCreated)
        async def h1(event: UserCreated) -> None:
            calls.append("h1")

        @bus.subscribe(UserCreated)
        async def h2(event: UserCreated) -> None:
            calls.append("h2")

        await bus.publish(UserCreated(user_id="u1"))
        assert set(calls) == {"h1", "h2"}

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_handler(self) -> None:
        bus = EventBus()
        calls: list[str] = []

        async def handler(event: UserCreated) -> None:
            calls.append("h")

        bus.subscribe(UserCreated, handler)
        bus.unsubscribe(UserCreated, handler)
        await bus.publish(UserCreated(user_id="u1"))
        assert calls == []

    @pytest.mark.asyncio
    async def test_handler_count(self) -> None:
        bus = EventBus()

        @bus.subscribe(UserCreated)
        async def h1(e: UserCreated) -> None:
            pass

        @bus.subscribe(OrderPlaced)
        async def h2(e: OrderPlaced) -> None:
            pass

        assert bus.handler_count == 2


class TestPriorities:
    @pytest.mark.asyncio
    async def test_lower_priority_runs_first(self) -> None:
        bus = EventBus()
        order: list[int] = []

        @bus.subscribe(UserCreated, priority=200)
        async def low(e: UserCreated) -> None:
            order.append(200)

        @bus.subscribe(UserCreated, priority=10)
        async def high(e: UserCreated) -> None:
            order.append(10)

        await bus.publish(UserCreated(user_id="u"))
        assert order[0] == 10


class TestRetries:
    @pytest.mark.asyncio
    async def test_handler_retried_on_failure(self) -> None:
        bus = EventBus()
        attempts: list[int] = [0]

        @bus.subscribe(UserCreated, max_retries=2)
        async def flaky(event: UserCreated) -> None:
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("temporary error")

        await bus.publish(UserCreated(user_id="u"))
        assert attempts[0] == 2


class TestMiddleware:
    @pytest.mark.asyncio
    async def test_middleware_called_before_handlers(self) -> None:
        bus = EventBus()
        log: list[str] = []

        class TracingMiddleware(EventMiddleware):
            async def __call__(self, event: DomainEvent, call_next: object) -> None:
                log.append("before")
                import asyncio
                await call_next(event)  # type: ignore[operator]
                log.append("after")

        bus.add_middleware(TracingMiddleware())

        @bus.subscribe(UserCreated)
        async def h(e: UserCreated) -> None:
            log.append("handler")

        await bus.publish(UserCreated(user_id="u"))
        assert log == ["before", "handler", "after"]

    @pytest.mark.asyncio
    async def test_logging_middleware_does_not_break(self) -> None:
        bus = EventBus()
        bus.add_middleware(LoggingMiddleware())

        @bus.subscribe(UserCreated)
        async def h(e: UserCreated) -> None:
            pass

        await bus.publish(UserCreated(user_id="u"))

    @pytest.mark.asyncio
    async def test_clear_handlers(self) -> None:
        bus = EventBus()
        calls: list[int] = []

        @bus.subscribe(UserCreated)
        async def h(e: UserCreated) -> None:
            calls.append(1)

        bus.clear_handlers(UserCreated)
        await bus.publish(UserCreated(user_id="u"))
        assert calls == []


class TestDomainEvent:
    def test_event_id_generated(self) -> None:
        e = UserCreated(user_id="u1")
        assert len(e.event_id) == 36

    def test_event_type_auto_set(self) -> None:
        e = UserCreated(user_id="u1")
        assert e.event_type == "UserCreated"

    def test_occurred_at_set(self) -> None:
        e = UserCreated(user_id="u1")
        assert e.occurred_at is not None

    def test_event_name_classmethod(self) -> None:
        assert UserCreated.event_name() == "UserCreated"

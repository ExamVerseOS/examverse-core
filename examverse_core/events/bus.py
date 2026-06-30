"""Async event bus — the publish/subscribe backbone of ExamVerseOS.

The :class:`EventBus` decouples event producers from consumers. Handlers
are invoked concurrently within a priority band. Middleware wraps every
publish call in a composable pipeline.

Example:
    >>> bus = EventBus()
    >>> @bus.subscribe(UserCreated)
    ... async def on_user_created(event: UserCreated) -> None:
    ...     print(event.user_id)
    >>> await bus.publish(UserCreated(user_id="abc", email="a@b.com"))
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable, Type, TypeVar

from examverse_core.events.base import DomainEvent
from examverse_core.events.middleware import EventMiddleware

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=DomainEvent)
Handler = Callable[[Any], Awaitable[None]]


class _HandlerEntry:
    """Internal container for a subscriber's handler and its priority.

    Attributes:
        handler: The async callable that processes the event.
        priority: Lower values run in earlier priority groups.
        max_retries: Number of retry attempts on handler failure.
    """

    __slots__ = ("handler", "priority", "max_retries")

    def __init__(self, handler: Handler, priority: int, max_retries: int) -> None:
        self.handler = handler
        self.priority = priority
        self.max_retries = max_retries


class EventBus:
    """Async publish/subscribe event bus with middleware and priority support.

    Handlers registered for the same event type are grouped by priority
    (lower number = higher priority) and invoked concurrently within each
    group. Groups are executed sequentially so that higher-priority handlers
    complete before lower-priority ones start.

    Middleware is applied in the order it was added via :meth:`add_middleware`.
    """

    def __init__(self) -> None:
        """Initialise an empty event bus."""
        self._handlers: dict[str, list[_HandlerEntry]] = defaultdict(list)
        self._middleware: list[EventMiddleware] = []

    def add_middleware(self, middleware: EventMiddleware) -> None:
        """Append a middleware to the processing pipeline.

        Middleware is executed in the order it is added.

        Args:
            middleware: An :class:`EventMiddleware` implementation.
        """
        self._middleware.append(middleware)

    def subscribe(
        self,
        event_type: Type[E],
        handler: Handler | None = None,
        *,
        priority: int = 100,
        max_retries: int = 0,
    ) -> Any:
        """Subscribe to an event type.

        Can be used as a direct call or as a decorator.

        Args:
            event_type: The :class:`DomainEvent` subclass to listen for.
            handler: Optional async callable. When omitted, returns a decorator.
            priority: Execution priority group (lower = earlier). Default: 100.
            max_retries: Number of times to retry a failing handler. Default: 0.

        Returns:
            The handler (or a decorator when ``handler`` is ``None``).

        Example:
            >>> @bus.subscribe(UserCreated, priority=10)
            ... async def handle(event: UserCreated) -> None: ...
        """
        def decorator(fn: Handler) -> Handler:
            key = event_type.event_name()
            entry = _HandlerEntry(handler=fn, priority=priority, max_retries=max_retries)
            self._handlers[key].append(entry)
            self._handlers[key].sort(key=lambda e: e.priority)
            logger.debug(
                "Subscribed handler",
                extra={"event_type": key, "handler": fn.__qualname__},
            )
            return fn

        if handler is not None:
            return decorator(handler)
        return decorator

    def unsubscribe(self, event_type: Type[E], handler: Handler) -> bool:
        """Remove a specific handler for an event type.

        Args:
            event_type: The event type to remove the handler from.
            handler: The exact callable that was previously subscribed.

        Returns:
            ``True`` if the handler was found and removed, ``False`` otherwise.
        """
        key = event_type.event_name()
        before = len(self._handlers[key])
        self._handlers[key] = [e for e in self._handlers[key] if e.handler is not handler]
        return len(self._handlers[key]) < before

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event through the middleware pipeline and invoke all handlers.

        Args:
            event: The domain event to dispatch.
        """
        pipeline = self._build_pipeline(event)
        await pipeline(event)

    def _build_pipeline(self, event: DomainEvent) -> Callable[[DomainEvent], Awaitable[None]]:
        """Construct the middleware + handler pipeline for a single publish call.

        Args:
            event: The event being dispatched (used only to build the chain).

        Returns:
            An awaitable callable that executes the full pipeline.
        """
        async def dispatch(evt: DomainEvent) -> None:
            await self._dispatch_to_handlers(evt)

        chain: Callable[[DomainEvent], Awaitable[None]] = dispatch
        for mw in reversed(self._middleware):
            _mw = mw
            _next = chain

            async def step(evt: DomainEvent, _m: EventMiddleware = _mw, _n: Any = _next) -> None:
                await _m(evt, _n)

            chain = step

        return chain

    async def _dispatch_to_handlers(self, event: DomainEvent) -> None:
        """Invoke all registered handlers for the event's type.

        Handlers are grouped by priority. Within each group they run
        concurrently via :func:`asyncio.gather`. Errors are caught and logged
        unless ``max_retries > 0``, in which case the handler is retried.

        Args:
            event: The event to dispatch.
        """
        key = event.event_type
        entries = self._handlers.get(key, [])
        if not entries:
            logger.debug("No handlers for event", extra={"event_type": key})
            return

        priority_groups: dict[int, list[_HandlerEntry]] = defaultdict(list)
        for entry in entries:
            priority_groups[entry.priority].append(entry)

        for priority in sorted(priority_groups):
            group = priority_groups[priority]
            tasks = [self._invoke_with_retry(entry, event) for entry in group]
            await asyncio.gather(*tasks)

    async def _invoke_with_retry(self, entry: _HandlerEntry, event: DomainEvent) -> None:
        """Invoke a single handler with retry logic.

        Args:
            entry: The handler entry including retry configuration.
            event: The event to pass to the handler.
        """
        attempts = 0
        while True:
            try:
                await entry.handler(event)
                return
            except Exception as exc:
                attempts += 1
                if attempts > entry.max_retries:
                    logger.error(
                        "Handler failed after retries",
                        extra={
                            "event_type": event.event_type,
                            "handler": entry.handler.__qualname__,
                            "attempts": attempts,
                            "error": str(exc),
                        },
                    )
                    return
                delay = 2 ** (attempts - 1) * 0.1
                logger.warning(
                    "Handler failed, retrying",
                    extra={
                        "event_type": event.event_type,
                        "handler": entry.handler.__qualname__,
                        "attempt": attempts,
                        "delay_s": delay,
                        "error": str(exc),
                    },
                )
                await asyncio.sleep(delay)

    def clear_handlers(self, event_type: Type[E] | None = None) -> None:
        """Remove handlers for a specific event type, or all handlers.

        Args:
            event_type: When provided, only clear handlers for this type.
                When ``None``, clear all registered handlers.
        """
        if event_type is None:
            self._handlers.clear()
        else:
            self._handlers.pop(event_type.event_name(), None)

    @property
    def handler_count(self) -> int:
        """Total number of registered handlers across all event types.

        Returns:
            Integer handler count.
        """
        return sum(len(v) for v in self._handlers.values())

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        Returns:
            String with event type count and handler count.
        """
        return (
            f"<EventBus event_types={len(self._handlers)} "
            f"handlers={self.handler_count}>"
        )

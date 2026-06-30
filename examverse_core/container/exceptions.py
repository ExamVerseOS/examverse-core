"""Exceptions raised by the ExamVerse DI container."""

from __future__ import annotations

from typing import Any, Type


class ContainerError(Exception):
    """Base class for all container-related errors."""


class ServiceNotFoundError(ContainerError):
    """Raised when a requested service type is not registered.

    Args:
        interface: The type that was requested but not found.
    """

    def __init__(self, interface: Type[Any]) -> None:
        super().__init__(f"No service registered for {interface!r}.")
        self.interface = interface


class CircularDependencyError(ContainerError):
    """Raised when a circular dependency is detected during resolution.

    Args:
        chain: The resolution chain at the point the cycle was detected.
    """

    def __init__(self, chain: list[Type[Any]]) -> None:
        names = " → ".join(t.__name__ for t in chain)
        super().__init__(f"Circular dependency detected: {names}")
        self.chain = chain


class ScopeError(ContainerError):
    """Raised when a scoped service is resolved outside an active scope."""

    def __init__(self) -> None:
        super().__init__(
            "Cannot resolve a scoped service outside an active scope. "
            "Use ServiceContainer.scope() context manager."
        )

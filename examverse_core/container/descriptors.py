"""Lifetime descriptors for the ExamVerse DI container.

Each descriptor controls how many instances of a service are created and
when those instances are disposed. Four lifetimes are supported:

- :class:`SingletonDescriptor` — one instance per container.
- :class:`TransientDescriptor` — new instance on every resolve.
- :class:`ScopedDescriptor` — one instance per logical scope (e.g. request).
- :class:`FactoryDescriptor` — delegates creation to a callable.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Callable, Type


class Lifetime(str, enum.Enum):
    """Enumeration of supported service lifetimes."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"
    FACTORY = "factory"


@dataclass(frozen=True)
class SingletonDescriptor:
    """One shared instance for the lifetime of the container.

    Attributes:
        interface: The abstract type (interface) used as the lookup key.
        implementation: The concrete type to instantiate once.
    """

    interface: Type[Any]
    implementation: Type[Any]
    lifetime: Lifetime = field(default=Lifetime.SINGLETON, init=False)


@dataclass(frozen=True)
class TransientDescriptor:
    """A new instance created on every :meth:`~ServiceContainer.resolve` call.

    Attributes:
        interface: The abstract type (interface) used as the lookup key.
        implementation: The concrete type to instantiate each time.
    """

    interface: Type[Any]
    implementation: Type[Any]
    lifetime: Lifetime = field(default=Lifetime.TRANSIENT, init=False)


@dataclass(frozen=True)
class ScopedDescriptor:
    """One instance per active scope (e.g. one per HTTP request).

    Attributes:
        interface: The abstract type (interface) used as the lookup key.
        implementation: The concrete type to instantiate per scope.
    """

    interface: Type[Any]
    implementation: Type[Any]
    lifetime: Lifetime = field(default=Lifetime.SCOPED, init=False)


@dataclass(frozen=True)
class FactoryDescriptor:
    """Delegates instantiation to a user-supplied callable.

    The factory receives the container as its only argument so it can
    resolve its own dependencies.

    Attributes:
        interface: The abstract type (interface) used as the lookup key.
        factory: Callable that accepts a :class:`~ServiceContainer` and returns an instance.
    """

    interface: Type[Any]
    factory: Callable[..., Any]
    lifetime: Lifetime = field(default=Lifetime.FACTORY, init=False)


Descriptor = SingletonDescriptor | TransientDescriptor | ScopedDescriptor | FactoryDescriptor
"""Union type alias for all descriptor variants."""

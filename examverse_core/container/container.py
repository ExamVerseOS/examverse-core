"""ExamVerse service container — the heart of the dependency injection system.

The :class:`ServiceContainer` is a full-featured DI container that supports
singleton, transient, scoped, and factory lifetimes with automatic constructor
injection via type hints.

Example:
    >>> from examverse_core.container import ServiceContainer
    >>> container = ServiceContainer()
    >>> container.bind_singleton(ICache, RedisCache)
    >>> cache = container.resolve(ICache)
"""

from __future__ import annotations

import contextlib
import threading
from contextvars import ContextVar
from typing import Any, Callable, Iterator, Type, TypeVar

from examverse_core.container.descriptors import (
    Descriptor,
    FactoryDescriptor,
    Lifetime,
    ScopedDescriptor,
    SingletonDescriptor,
    TransientDescriptor,
)
from examverse_core.container.exceptions import (
    ScopeError,
    ServiceNotFoundError,
)
from examverse_core.container.resolver import DependencyResolver

T = TypeVar("T")

_scope_store: ContextVar[dict[Type[Any], Any] | None] = ContextVar(
    "_scope_store", default=None
)


class ServiceContainer:
    """Application-level DI container with four lifetime strategies.

    Supports:
    - **Singleton** — one shared instance per container.
    - **Transient** — new instance on every resolve call.
    - **Scoped** — one instance per :meth:`scope` context.
    - **Factory** — delegates instantiation to a callable.
    - **Instance** — register a pre-built instance as a singleton.

    All binding methods are chainable and thread-safe for singleton lookups.
    """

    def __init__(self) -> None:
        """Initialise an empty container."""
        self._descriptors: dict[Type[Any], Descriptor] = {}
        self._singletons: dict[Type[Any], Any] = {}
        self._lock = threading.RLock()
        self._resolver = DependencyResolver(self)

    def bind_singleton(self, interface: Type[T], implementation: Type[T]) -> ServiceContainer:
        """Register a singleton binding.

        Args:
            interface: The abstract type used as the lookup key.
            implementation: The concrete type to instantiate once.

        Returns:
            The container itself for fluent chaining.
        """
        self._descriptors[interface] = SingletonDescriptor(
            interface=interface, implementation=implementation
        )
        return self

    def bind_transient(self, interface: Type[T], implementation: Type[T]) -> ServiceContainer:
        """Register a transient binding.

        Args:
            interface: The abstract type used as the lookup key.
            implementation: The concrete type to instantiate each time.

        Returns:
            The container itself for fluent chaining.
        """
        self._descriptors[interface] = TransientDescriptor(
            interface=interface, implementation=implementation
        )
        return self

    def bind_scoped(self, interface: Type[T], implementation: Type[T]) -> ServiceContainer:
        """Register a scoped binding.

        Args:
            interface: The abstract type used as the lookup key.
            implementation: The concrete type to instantiate per scope.

        Returns:
            The container itself for fluent chaining.
        """
        self._descriptors[interface] = ScopedDescriptor(
            interface=interface, implementation=implementation
        )
        return self

    def bind_factory(
        self, interface: Type[T], factory: Callable[[ServiceContainer], T]
    ) -> ServiceContainer:
        """Register a factory binding.

        Args:
            interface: The abstract type used as the lookup key.
            factory: A callable ``(container) -> T`` that produces the service.

        Returns:
            The container itself for fluent chaining.
        """
        self._descriptors[interface] = FactoryDescriptor(
            interface=interface, factory=factory
        )
        return self

    def bind_instance(self, interface: Type[T], instance: T) -> ServiceContainer:
        """Register a pre-built instance as a singleton.

        Args:
            interface: The abstract type used as the lookup key.
            instance: The pre-built object to return on every resolve.

        Returns:
            The container itself for fluent chaining.
        """
        self._descriptors[interface] = SingletonDescriptor(
            interface=interface, implementation=type(instance)
        )
        self._singletons[interface] = instance
        return self

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service by its interface type.

        Args:
            interface: The abstract type (or concrete class) to resolve.

        Returns:
            A fully-wired instance of the requested service.

        Raises:
            ServiceNotFoundError: If no binding exists for ``interface``.
            CircularDependencyError: If a circular dependency is detected.
            ScopeError: If a scoped service is resolved outside a scope.
        """
        return self._resolve_by_type(interface)  # type: ignore[return-value]

    def _resolve_by_type(
        self,
        interface: Type[Any],
        resolution_chain: list[Type[Any]] | None = None,
    ) -> Any:
        """Internal resolution — respects lifetime and scope rules.

        Args:
            interface: The type to resolve.
            resolution_chain: Tracks the resolution call stack for cycle detection.

        Returns:
            A fully-wired instance.

        Raises:
            ServiceNotFoundError: When the type is not registered.
        """
        descriptor = self._descriptors.get(interface)
        if descriptor is None:
            raise ServiceNotFoundError(interface)

        if descriptor.lifetime == Lifetime.SINGLETON:
            with self._lock:
                if interface not in self._singletons:
                    assert isinstance(descriptor, SingletonDescriptor)
                    self._singletons[interface] = self._resolver.resolve(
                        descriptor.implementation,
                        resolution_chain=resolution_chain,
                    )
            return self._singletons[interface]

        if descriptor.lifetime == Lifetime.TRANSIENT:
            assert isinstance(descriptor, TransientDescriptor)
            return self._resolver.resolve(
                descriptor.implementation, resolution_chain=resolution_chain
            )

        if descriptor.lifetime == Lifetime.SCOPED:
            store = _scope_store.get()
            if store is None:
                raise ScopeError()
            if interface not in store:
                assert isinstance(descriptor, ScopedDescriptor)
                store[interface] = self._resolver.resolve(
                    descriptor.implementation, resolution_chain=resolution_chain
                )
            return store[interface]

        if descriptor.lifetime == Lifetime.FACTORY:
            assert isinstance(descriptor, FactoryDescriptor)
            return descriptor.factory(self)

        raise ServiceNotFoundError(interface)  # pragma: no cover

    def is_registered(self, interface: Type[Any]) -> bool:
        """Check whether a type is registered in the container.

        Args:
            interface: The type to check.

        Returns:
            ``True`` if registered, ``False`` otherwise.
        """
        return interface in self._descriptors

    @contextlib.contextmanager
    def scope(self) -> Iterator[ServiceContainer]:
        """Create a new dependency injection scope.

        Scoped services resolve to a single instance within the scope and
        are discarded when the scope exits.

        Yields:
            The container itself (for convenient ``with container.scope() as c:`` use).

        Example:
            >>> with container.scope():
            ...     svc = container.resolve(IUnitOfWork)
        """
        token = _scope_store.set({})
        try:
            yield self
        finally:
            _scope_store.reset(token)

    def clear(self) -> None:
        """Remove all bindings and cached singletons.

        Intended for use in tests where a fresh container is needed between
        test cases.
        """
        self._descriptors.clear()
        self._singletons.clear()

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        Returns:
            String with binding count.
        """
        return f"<ServiceContainer bindings={len(self._descriptors)}>"

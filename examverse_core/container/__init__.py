"""ExamVerse DI container — singleton, transient, scoped, and factory lifetimes."""

from examverse_core.container.container import ServiceContainer
from examverse_core.container.descriptors import (
    FactoryDescriptor,
    Lifetime,
    ScopedDescriptor,
    SingletonDescriptor,
    TransientDescriptor,
)
from examverse_core.container.exceptions import (
    CircularDependencyError,
    ContainerError,
    ScopeError,
    ServiceNotFoundError,
)

__all__ = [
    "ServiceContainer",
    "Lifetime",
    "SingletonDescriptor",
    "TransientDescriptor",
    "ScopedDescriptor",
    "FactoryDescriptor",
    "ContainerError",
    "ServiceNotFoundError",
    "CircularDependencyError",
    "ScopeError",
]

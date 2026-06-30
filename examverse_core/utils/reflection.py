"""Reflection utilities for runtime introspection in ExamVerseOS.

Example:
    >>> import_class("examverse_core.events.base.DomainEvent")
    <class 'examverse_core.events.base.DomainEvent'>
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any, Type, TypeVar

T = TypeVar("T")


def import_class(dotted_path: str) -> Type[Any]:
    """Import and return a class from a dotted module path.

    Args:
        dotted_path: Fully-qualified class path
            (e.g. ``"examverse_core.events.base.DomainEvent"``).

    Returns:
        The class object.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the class name is not found in the module.
        TypeError: If the resolved attribute is not a class.
    """
    module_path, _, class_name = dotted_path.rpartition(".")
    if not module_path:
        raise ImportError(f"Invalid dotted path: {dotted_path!r}")
    module = importlib.import_module(module_path)
    obj = getattr(module, class_name)
    if not isinstance(obj, type):
        raise TypeError(f"{dotted_path!r} is not a class — got {type(obj).__name__}")
    return obj


def get_subclasses(base: Type[T], *, recursive: bool = True) -> list[Type[T]]:
    """Collect all concrete (non-abstract) subclasses of a base class.

    Args:
        base: The parent class to search from.
        recursive: When ``True``, recurse into subclass trees.

    Returns:
        List of concrete subclasses (those not marked as abstract).
    """
    result: list[Type[T]] = []
    for sub in base.__subclasses__():
        if not inspect.isabstract(sub):
            result.append(sub)
        if recursive:
            result.extend(get_subclasses(sub, recursive=True))
    return result


def get_class_attributes(cls: type) -> dict[str, Any]:
    """Return a dictionary of a class's own (non-inherited) attributes.

    Args:
        cls: The class to inspect.

    Returns:
        Dict of attribute name → value for attributes defined directly on ``cls``.
    """
    return {
        k: v
        for k, v in vars(cls).items()
        if not k.startswith("__") or k in ("__annotations__",)
    }


def is_async_callable(obj: Any) -> bool:
    """Check whether an object is an async callable.

    Args:
        obj: Any Python object.

    Returns:
        ``True`` if the object is a coroutine function or async generator function.
    """
    return inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj)


def get_module_name(obj: Any) -> str:
    """Return the fully-qualified module name of an object.

    Args:
        obj: Any Python object (class, function, etc.).

    Returns:
        The ``__module__`` attribute string, or ``"unknown"`` if unavailable.
    """
    return getattr(obj, "__module__", "unknown")

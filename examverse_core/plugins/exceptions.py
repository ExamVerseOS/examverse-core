"""Exceptions raised by the ExamVerse plugin system."""

from __future__ import annotations


class PluginError(Exception):
    """Base class for all plugin-related errors."""


class DuplicatePluginError(PluginError):
    """Raised when a plugin with the same name is registered twice.

    Args:
        name: The duplicate plugin name.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"Plugin {name!r} is already registered.")
        self.name = name


class MissingPluginDependencyError(PluginError):
    """Raised when a plugin declares a dependency that is not registered.

    Args:
        name: The missing dependency plugin name.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"Required plugin dependency {name!r} is not registered.")
        self.name = name


class PluginCycleError(PluginError):
    """Raised when circular dependencies are detected in the plugin graph.

    Args:
        name: The plugin name where the cycle was detected.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f"Circular dependency detected while resolving plugin {name!r}.")
        self.name = name


class PluginInitializationError(PluginError):
    """Raised when a plugin fails during :meth:`Plugin.initialize`.

    Args:
        name: The plugin name that failed.
        cause: The underlying exception.
    """

    def __init__(self, name: str, cause: Exception) -> None:
        super().__init__(f"Plugin {name!r} failed to initialize: {cause}")
        self.name = name
        self.cause = cause

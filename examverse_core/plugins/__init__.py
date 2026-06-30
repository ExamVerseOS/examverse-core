"""ExamVerse plugin system — base classes, registry, and exceptions."""

from examverse_core.plugins.base import Plugin, PluginMetadata
from examverse_core.plugins.exceptions import (
    DuplicatePluginError,
    MissingPluginDependencyError,
    PluginCycleError,
    PluginError,
    PluginInitializationError,
)
from examverse_core.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginError",
    "DuplicatePluginError",
    "MissingPluginDependencyError",
    "PluginCycleError",
    "PluginInitializationError",
]

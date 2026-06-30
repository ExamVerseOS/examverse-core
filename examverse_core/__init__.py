"""ExamVerse Core — Shared runtime foundation for the ExamVerseOS ecosystem.

This package provides the foundational building blocks that every ExamVerse
service depends on: plugin system, dependency injection, event bus, AI
abstractions, domain models, configuration, structured logging, security
utilities, validators, and general-purpose utilities.

Example:
    >>> from examverse_core import PluginRegistry, ServiceContainer, EventBus
    >>> from examverse_core.config import CoreSettings
    >>> settings = CoreSettings()
    >>> container = ServiceContainer()
    >>> bus = EventBus()
    >>> registry = PluginRegistry(container=container, bus=bus)
"""

from examverse_core.container.container import ServiceContainer
from examverse_core.events.bus import EventBus
from examverse_core.plugins.base import Plugin, PluginMetadata
from examverse_core.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "ServiceContainer",
    "EventBus",
]

__version__ = "0.1.0"
__author__ = "ExamVerse Team"
__license__ = "MIT"

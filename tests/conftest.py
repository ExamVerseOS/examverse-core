"""Shared pytest fixtures for the examverse-core test suite."""

from __future__ import annotations

import pytest

from examverse_core.container.container import ServiceContainer
from examverse_core.events.bus import EventBus
from examverse_core.plugins.registry import PluginRegistry


@pytest.fixture
def container() -> ServiceContainer:
    """Return a fresh, empty DI container for each test."""
    return ServiceContainer()


@pytest.fixture
def bus() -> EventBus:
    """Return a fresh event bus for each test."""
    return EventBus()


@pytest.fixture
def registry(container: ServiceContainer, bus: EventBus) -> PluginRegistry:
    """Return a fresh plugin registry backed by the container and bus fixtures."""
    return PluginRegistry(container=container, bus=bus)

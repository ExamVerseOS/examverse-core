"""Tests for Plugin base class and PluginMetadata."""

from __future__ import annotations

import pytest

from examverse_core.container.container import ServiceContainer
from examverse_core.events.bus import EventBus
from examverse_core.plugins.base import Plugin, PluginMetadata


def make_plugin(
    name: str = "test-plugin",
    version: str = "1.0.0",
    requires: list[str] | None = None,
) -> type[Plugin]:
    """Factory that creates a concrete Plugin subclass for testing."""

    class _ConcretePlugin(Plugin):
        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name=name,
                version=version,
                requires=requires or [],
            )

        async def initialize(self) -> None:
            pass

        async def shutdown(self) -> None:
            pass

    return _ConcretePlugin


class TestPluginMetadata:
    def test_valid_metadata(self) -> None:
        meta = PluginMetadata(name="my-plugin", version="1.0.0")
        assert meta.name == "my-plugin"
        assert meta.version == "1.0.0"

    def test_invalid_name_raises(self) -> None:
        with pytest.raises(Exception):
            PluginMetadata(name="My Plugin!", version="1.0.0")

    def test_requires_defaults_empty(self) -> None:
        meta = PluginMetadata(name="p", version="0.1.0")
        assert meta.requires == []

    def test_metadata_is_frozen(self) -> None:
        meta = PluginMetadata(name="p", version="1.0.0")
        with pytest.raises(Exception):
            meta.name = "other"  # type: ignore[misc]


class TestPlugin:
    def test_repr(self) -> None:
        cls = make_plugin("my-plugin", "2.0.0")
        container = ServiceContainer()
        bus = EventBus()
        plugin = cls(container=container, bus=bus)
        assert "my-plugin" in repr(plugin)
        assert "2.0.0" in repr(plugin)

    def test_get_config_returns_default(self) -> None:
        cls = make_plugin()
        plugin = cls(container=ServiceContainer(), bus=EventBus(), config={"key": "val"})
        assert plugin.get_config("key") == "val"
        assert plugin.get_config("missing", "default") == "default"

    def test_register_services_noop(self) -> None:
        cls = make_plugin()
        plugin = cls(container=ServiceContainer(), bus=EventBus())
        plugin.register_services()  # must not raise

    def test_register_events_noop(self) -> None:
        cls = make_plugin()
        plugin = cls(container=ServiceContainer(), bus=EventBus())
        plugin.register_events()  # must not raise

    def test_register_routes_noop(self) -> None:
        cls = make_plugin()
        plugin = cls(container=ServiceContainer(), bus=EventBus())
        plugin.register_routes()  # must not raise

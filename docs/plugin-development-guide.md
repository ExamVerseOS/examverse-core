# Plugin Development Guide

This guide walks you through building, testing, and distributing a plugin for the ExamVerseOS ecosystem.

---

## Prerequisites

- Python 3.12+
- Poetry
- `examverse-core` installed as a dependency

---

## 1. Create a New Plugin Package

```bash
poetry new examverse-my-plugin
cd examverse-my-plugin
poetry add examverse-core
```

---

## 2. Implement the Plugin Class

Every plugin extends `examverse_core.plugins.Plugin` and implements five lifecycle methods:

```python
# examverse_my_plugin/plugin.py
from __future__ import annotations

from examverse_core.plugins import Plugin, PluginMetadata


class MyPlugin(Plugin):
    """My feature plugin for ExamVerseOS."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="Provides my feature",
            author="My Team",
            requires=[],          # list plugin names this depends on
            tags=["feature"],
        )

    def register_services(self) -> None:
        """Bind services into the DI container."""
        from examverse_my_plugin.service import MyService, IMyService
        self._container.bind_singleton(IMyService, MyService)

    def register_events(self) -> None:
        """Subscribe to domain events."""
        from examverse_core.models.exam import QuestionCreated
        self._bus.subscribe(QuestionCreated, self._on_question_created)

    def register_routes(self) -> None:
        """Register HTTP routes (optional)."""
        # Hook into your web framework here

    async def initialize(self) -> None:
        """Perform async startup (open connections, etc.)."""
        from examverse_my_plugin.service import IMyService
        svc = self._container.resolve(IMyService)
        await svc.connect()

    async def shutdown(self) -> None:
        """Release resources gracefully."""
        from examverse_my_plugin.service import IMyService
        svc = self._container.resolve(IMyService)
        await svc.disconnect()

    async def _on_question_created(self, event: object) -> None:
        # handle the event
        pass
```

---

## 3. Declare the Entry Point

Register your plugin so ExamVerse discovers it automatically:

```toml
# pyproject.toml
[tool.poetry.plugins."examverse.plugins"]
my-plugin = "examverse_my_plugin.plugin:MyPlugin"
```

No manual registration is needed. Once the package is installed, `PluginRegistry.load_from_entry_points()` will find it.

---

## 4. Declare Dependencies Between Plugins

If your plugin depends on another plugin being initialised first:

```python
@property
def metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        requires=["cache", "auth"],   # these plugins will initialise first
    )
```

The registry resolves a topological order automatically and raises `PluginCycleError` if a circular dependency is detected.

---

## 5. Access Plugin Configuration

```python
# In your plugin
timeout = self.get_config("timeout_seconds", default=30)
endpoint = self.get_config("endpoint_url")
```

Configuration is supplied by the host application:

```python
registry.register(
    MyPlugin,
    config={"timeout_seconds": 60, "endpoint_url": "https://my.service.io"},
)
```

Or via `CoreSettings.plugins.configs["my-plugin"]`.

---

## 6. Write Tests

```python
# tests/test_plugin.py
import pytest
from examverse_core.container import ServiceContainer
from examverse_core.events import EventBus
from examverse_my_plugin.plugin import MyPlugin


@pytest.fixture
def plugin() -> MyPlugin:
    return MyPlugin(
        container=ServiceContainer(),
        bus=EventBus(),
        config={"endpoint_url": "http://localhost"},
    )


def test_metadata(plugin: MyPlugin) -> None:
    assert plugin.metadata.name == "my-plugin"
    assert plugin.metadata.version == "1.0.0"


def test_register_services(plugin: MyPlugin) -> None:
    plugin.register_services()
    from examverse_my_plugin.service import IMyService
    assert plugin._container.is_registered(IMyService)


@pytest.mark.asyncio
async def test_lifecycle(plugin: MyPlugin) -> None:
    plugin.register_services()
    await plugin.initialize()
    await plugin.shutdown()
```

---

## 7. Publish

```bash
poetry build
poetry publish --repository examverse-internal
```

Once published and installed in any ExamVerse service, the plugin is discovered and loaded automatically.

---

## Plugin Lifecycle Summary

```
registry.load_from_entry_points()   # discovers plugin class
        │
registry.register(MyPlugin)         # instantiates with container + bus
        │
topological_order()                 # sorts by requires:
        │
register_services()  ← all plugins  # bind DI services
register_events()    ← all plugins  # subscribe event handlers
register_routes()    ← all plugins  # register HTTP routes
        │
initialize()  ← ordered            # async startup, one by one
        │
[application runs]
        │
shutdown()  ← reverse order        # async teardown
```

---

## Available Hook Points

| Method | When called | Use for |
|---|---|---|
| `register_services()` | Before any `initialize()` | Binding DI services |
| `register_events()` | Before any `initialize()` | Subscribing event handlers |
| `register_routes()` | Before any `initialize()` | Adding HTTP routes |
| `initialize()` | After all services/events registered | Opening connections, background tasks |
| `shutdown()` | On application shutdown (reverse order) | Closing connections, flushing queues |

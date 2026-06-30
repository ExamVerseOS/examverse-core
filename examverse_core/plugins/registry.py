"""Plugin registry — discovers, orders, and manages the lifecycle of all plugins.

The :class:`PluginRegistry` is the central coordinator for the ExamVerse
plugin system. It performs dependency-sorted loading and provides a clean
API for querying loaded plugins at runtime.

Example:
    >>> registry = PluginRegistry(container=container, bus=bus)
    >>> registry.load_from_entry_points(group="examverse.plugins")
    >>> await registry.initialize_all()
    >>> # application runs …
    >>> await registry.shutdown_all()
"""

from __future__ import annotations

import importlib
import importlib.metadata
import logging
from typing import TYPE_CHECKING, Any, Iterator, Type

from examverse_core.plugins.base import Plugin, PluginMetadata
from examverse_core.plugins.exceptions import (
    DuplicatePluginError,
    MissingPluginDependencyError,
    PluginCycleError,
    PluginInitializationError,
)

if TYPE_CHECKING:
    from examverse_core.container.container import ServiceContainer
    from examverse_core.events.bus import EventBus

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Discovers, orders, and manages the lifecycle of all ExamVerse plugins.

    Plugins are discovered automatically from Python entry points, explicit
    class registration, or module paths. They are initialised in
    dependency-topological order and shut down in reverse order.

    Attributes:
        _container: The shared DI service container.
        _bus: The shared async event bus.
        _plugins: Ordered mapping of plugin name → plugin instance.
    """

    def __init__(self, container: ServiceContainer, bus: EventBus) -> None:
        """Create a new registry backed by the given container and bus.

        Args:
            container: Shared application-level DI container.
            bus: Shared application-level async event bus.
        """
        self._container = container
        self._bus = bus
        self._plugins: dict[str, Plugin] = {}
        self._initialized: bool = False

    def register(
        self,
        plugin_class: Type[Plugin],
        config: dict[str, Any] | None = None,
    ) -> None:
        """Register a plugin class directly.

        Args:
            plugin_class: A concrete subclass of :class:`Plugin`.
            config: Optional plugin-specific configuration dict.

        Raises:
            DuplicatePluginError: If a plugin with the same name is already registered.
        """
        instance = plugin_class(
            container=self._container,
            bus=self._bus,
            config=config,
        )
        name = instance.metadata.name
        if name in self._plugins:
            raise DuplicatePluginError(name)
        self._plugins[name] = instance
        logger.debug("Registered plugin", extra={"plugin": name})

    def load_from_entry_points(self, group: str = "examverse.plugins") -> None:
        """Auto-discover plugins declared as Python package entry points.

        Any installed package that declares an entry point in the given group
        is loaded and registered automatically. The entry point value must be
        a dotted path to a :class:`Plugin` subclass.

        Args:
            group: The entry point group name to scan (default: ``"examverse.plugins"``).
        """
        try:
            eps = importlib.metadata.entry_points(group=group)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to read entry points", extra={"group": group, "error": str(exc)})
            return

        for ep in eps:
            try:
                plugin_class: Type[Plugin] = ep.load()
                self.register(plugin_class)
                logger.info(
                    "Loaded plugin from entry point",
                    extra={"entry_point": ep.name, "plugin": plugin_class.__name__},
                )
            except DuplicatePluginError:
                raise
            except Exception as exc:
                logger.error(
                    "Failed to load plugin entry point",
                    extra={"entry_point": ep.name, "error": str(exc)},
                )

    def load_from_module(self, dotted_path: str, config: dict[str, Any] | None = None) -> None:
        """Load a single plugin from a dotted module path.

        Args:
            dotted_path: E.g. ``"my_package.plugins.search.SearchPlugin"``.
            config: Optional plugin configuration.

        Raises:
            ImportError: If the module or class cannot be imported.
            TypeError: If the resolved object is not a Plugin subclass.
        """
        module_path, _, class_name = dotted_path.rpartition(".")
        module = importlib.import_module(module_path)
        plugin_class: Type[Plugin] = getattr(module, class_name)
        if not (isinstance(plugin_class, type) and issubclass(plugin_class, Plugin)):
            raise TypeError(f"{dotted_path!r} is not a Plugin subclass")
        self.register(plugin_class, config=config)

    def _topological_order(self) -> list[Plugin]:
        """Return plugins sorted by dependency order (dependencies first).

        Returns:
            List of plugins in safe initialisation order.

        Raises:
            MissingPluginDependencyError: If a declared dependency is not registered.
            PluginCycleError: If circular dependencies are detected.
        """
        visited: set[str] = set()
        visiting: set[str] = set()
        order: list[Plugin] = []

        def visit(name: str) -> None:
            if name in visiting:
                raise PluginCycleError(name)
            if name in visited:
                return
            plugin = self._plugins.get(name)
            if plugin is None:
                raise MissingPluginDependencyError(name)
            visiting.add(name)
            for dep in plugin.metadata.requires:
                visit(dep)
            visiting.discard(name)
            visited.add(name)
            order.append(plugin)

        for name in list(self._plugins):
            visit(name)

        return order

    async def initialize_all(self) -> None:
        """Register services/events for all plugins then initialize each one.

        Plugins are initialised in dependency-topological order. If any plugin
        fails, the error is raised immediately; already-initialised plugins are
        NOT automatically shut down (call :meth:`shutdown_all` in your error
        handler).

        Raises:
            PluginInitializationError: Wraps any exception raised during initialization.
        """
        ordered = self._topological_order()

        for plugin in ordered:
            plugin.register_services()

        for plugin in ordered:
            plugin.register_events()

        for plugin in ordered:
            plugin.register_routes()

        for plugin in ordered:
            name = plugin.metadata.name
            try:
                await plugin.initialize()
                logger.info("Plugin initialized", extra={"plugin": name})
            except Exception as exc:
                raise PluginInitializationError(name, cause=exc) from exc

        self._initialized = True

    async def shutdown_all(self) -> None:
        """Shut down all plugins in reverse initialisation order.

        Errors during shutdown are logged but do not prevent other plugins
        from shutting down.
        """
        ordered = list(reversed(self._topological_order()))
        for plugin in ordered:
            name = plugin.metadata.name
            try:
                await plugin.shutdown()
                logger.info("Plugin shut down", extra={"plugin": name})
            except Exception as exc:
                logger.error(
                    "Error during plugin shutdown",
                    extra={"plugin": name, "error": str(exc)},
                )

    def get(self, name: str) -> Plugin | None:
        """Retrieve a loaded plugin by name.

        Args:
            name: The plugin's unique name.

        Returns:
            The :class:`Plugin` instance, or ``None`` if not found.
        """
        return self._plugins.get(name)

    def all(self) -> Iterator[Plugin]:
        """Iterate over all registered plugins.

        Yields:
            Each registered :class:`Plugin` instance.
        """
        yield from self._plugins.values()

    def metadata_for(self, name: str) -> PluginMetadata | None:
        """Return the metadata for a plugin without exposing the instance.

        Args:
            name: The plugin's unique name.

        Returns:
            :class:`PluginMetadata` or ``None`` if not found.
        """
        plugin = self._plugins.get(name)
        return plugin.metadata if plugin else None

    @property
    def names(self) -> list[str]:
        """Return a sorted list of all registered plugin names.

        Returns:
            Sorted list of plugin name strings.
        """
        return sorted(self._plugins)

    @property
    def is_initialized(self) -> bool:
        """True after :meth:`initialize_all` completes successfully.

        Returns:
            Boolean initialization state.
        """
        return self._initialized

    def __len__(self) -> int:
        """Return the number of registered plugins.

        Returns:
            Plugin count.
        """
        return len(self._plugins)

    def __repr__(self) -> str:
        """Return developer-friendly representation.

        Returns:
            String with plugin count and names.
        """
        return f"<PluginRegistry plugins={self.names!r}>"

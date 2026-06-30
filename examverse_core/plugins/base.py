"""Base plugin interface and metadata for the ExamVerse plugin system.

Every plugin in the ExamVerseOS ecosystem must implement :class:`Plugin`
and declare its :class:`PluginMetadata`. The framework discovers and loads
plugins automatically — no manual registration is required.

Example:
    >>> from examverse_core.plugins.base import Plugin, PluginMetadata
    >>> class MyPlugin(Plugin):
    ...     @property
    ...     def metadata(self) -> PluginMetadata:
    ...         return PluginMetadata(name="my-plugin", version="1.0.0")
    ...     async def initialize(self) -> None:
    ...         pass
    ...     async def shutdown(self) -> None:
    ...         pass
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from examverse_core.container.container import ServiceContainer
    from examverse_core.events.bus import EventBus


class PluginMetadata(BaseModel):
    """Immutable descriptor for a plugin's identity and requirements.

    Attributes:
        name: Unique snake_case identifier for the plugin.
        version: Semantic version string (e.g. "1.2.3").
        description: Human-readable summary of what the plugin provides.
        author: Author name or team.
        requires: List of plugin names this plugin depends on.
        tags: Free-form labels used by the registry for filtering.
        config_schema: Optional JSON Schema dict describing plugin configuration.
    """

    name: str = Field(..., pattern=r"^[a-z][a-z0-9_-]*$", description="Unique plugin identifier")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+", description="Semantic version")
    description: str = Field(default="", description="Human-readable description")
    author: str = Field(default="", description="Author name or team")
    requires: list[str] = Field(default_factory=list, description="Plugin dependencies")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    config_schema: dict[str, Any] | None = Field(
        default=None, description="JSON Schema for plugin config"
    )

    model_config = {"frozen": True}


class Plugin(abc.ABC):
    """Abstract base class every ExamVerse plugin must implement.

    The lifecycle of a plugin is:
        1. Instantiation by the plugin loader.
        2. :meth:`register_services` — bind types into the DI container.
        3. :meth:`register_events` — subscribe to domain events.
        4. :meth:`register_routes` — expose HTTP routes (optional).
        5. :meth:`initialize` — start background tasks, open connections, etc.
        6. Application runs.
        7. :meth:`shutdown` — release resources gracefully.
    """

    def __init__(
        self,
        container: ServiceContainer,
        bus: EventBus,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialise the plugin with shared infrastructure references.

        Args:
            container: The application-level DI service container.
            bus: The application-level async event bus.
            config: Optional plugin-specific configuration dict.
        """
        self._container = container
        self._bus = bus
        self._config: dict[str, Any] = config or {}

    @property
    @abc.abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the immutable descriptor for this plugin.

        Returns:
            A :class:`PluginMetadata` instance describing this plugin.
        """

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Start the plugin — open connections, spawn background tasks, etc.

        This method is called after all plugins have registered their services
        and events, so it is safe to resolve dependencies from ``self._container``.

        Raises:
            PluginInitializationError: When the plugin cannot start successfully.
        """

    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Stop the plugin and release all acquired resources.

        Must be idempotent — safe to call even if :meth:`initialize` was never
        called or failed partway through.
        """

    def register_services(self) -> None:
        """Bind services into the DI container before ``initialize`` is called.

        Override this method to register interfaces and implementations.
        The default implementation is a no-op.

        Example:
            >>> def register_services(self) -> None:
            ...     self._container.bind_singleton(MyInterface, MyImpl)
        """

    def register_events(self) -> None:
        """Subscribe event handlers on the event bus.

        Override this method to subscribe to domain events.
        The default implementation is a no-op.

        Example:
            >>> def register_events(self) -> None:
            ...     self._bus.subscribe(UserCreated, self._on_user_created)
        """

    def register_routes(self) -> None:
        """Register HTTP routes with the application router (optional).

        Override when the plugin needs to expose HTTP endpoints.
        The default implementation is a no-op.
        """

    def get_config(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration key to look up.
            default: Value returned when the key is absent.

        Returns:
            The configuration value or ``default``.
        """
        return self._config.get(key, default)

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        Returns:
            String representation including name and version.
        """
        meta = self.metadata
        return f"<Plugin name={meta.name!r} version={meta.version!r}>"

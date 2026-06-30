"""Automatic dependency resolver for the ExamVerse DI container.

The resolver inspects constructor type hints to determine which services
to inject, supporting both positional and keyword arguments. Resolution
is recursive: dependencies of dependencies are resolved automatically.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Type, get_type_hints

from examverse_core.container.exceptions import CircularDependencyError

if TYPE_CHECKING:
    from examverse_core.container.container import ServiceContainer


class DependencyResolver:
    """Resolves constructor dependencies using type-hint introspection.

    Attributes:
        _container: The container used to resolve nested dependencies.
    """

    def __init__(self, container: ServiceContainer) -> None:
        """Create a resolver bound to the given container.

        Args:
            container: The service container for recursive resolution.
        """
        self._container = container

    def resolve(
        self,
        implementation: Type[Any],
        resolution_chain: list[Type[Any]] | None = None,
    ) -> Any:
        """Instantiate ``implementation`` with auto-resolved constructor args.

        Args:
            implementation: The concrete class to instantiate.
            resolution_chain: Internal list tracking the current call stack
                to detect circular dependencies.

        Returns:
            A fully-wired instance of ``implementation``.

        Raises:
            CircularDependencyError: If a circular dependency is detected.
        """
        chain = resolution_chain or []

        if implementation in chain:
            raise CircularDependencyError(chain + [implementation])

        chain = chain + [implementation]

        try:
            hints = get_type_hints(implementation.__init__)
        except Exception:
            hints = {}

        sig = inspect.signature(implementation.__init__)
        kwargs: dict[str, Any] = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            if param.annotation is inspect.Parameter.empty:
                continue
            hint = hints.get(param_name)
            if hint is None:
                continue
            try:
                resolved = self._container._resolve_by_type(hint, resolution_chain=chain)
                kwargs[param_name] = resolved
            except Exception:
                if param.default is not inspect.Parameter.empty:
                    continue
                raise

        return implementation(**kwargs)

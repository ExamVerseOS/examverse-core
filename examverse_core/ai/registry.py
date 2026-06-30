"""Provider registry — manages AI provider registrations at runtime.

The :class:`ProviderRegistry` is the single source of truth for which
LLM and embedding providers are available. Concrete implementations are
registered by AI plugins; core code resolves providers by name.

Example:
    >>> registry = ProviderRegistry()
    >>> registry.register_llm("openai", my_openai_provider)
    >>> provider = registry.get_llm("openai")
"""

from __future__ import annotations

import logging

from examverse_core.ai.interfaces import EmbeddingProvider, LLMProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Central registry for LLM and embedding providers.

    Attributes:
        _llm_providers: Map of provider name → :class:`LLMProvider`.
        _embedding_providers: Map of provider name → :class:`EmbeddingProvider`.
        _default_llm: Name of the default LLM provider (or ``None``).
        _default_embedding: Name of the default embedding provider (or ``None``).
    """

    def __init__(self) -> None:
        """Initialise an empty registry."""
        self._llm_providers: dict[str, LLMProvider] = {}
        self._embedding_providers: dict[str, EmbeddingProvider] = {}
        self._default_llm: str | None = None
        self._default_embedding: str | None = None

    def register_llm(
        self,
        name: str,
        provider: LLMProvider,
        *,
        set_default: bool = False,
    ) -> None:
        """Register an LLM provider.

        Args:
            name: Unique provider identifier (e.g. ``"openai"``).
            provider: The :class:`LLMProvider` implementation.
            set_default: If ``True``, set this as the default provider.
        """
        self._llm_providers[name] = provider
        if set_default or self._default_llm is None:
            self._default_llm = name
        logger.info("Registered LLM provider", extra={"provider": name})

    def register_embedding(
        self,
        name: str,
        provider: EmbeddingProvider,
        *,
        set_default: bool = False,
    ) -> None:
        """Register an embedding provider.

        Args:
            name: Unique provider identifier.
            provider: The :class:`EmbeddingProvider` implementation.
            set_default: If ``True``, set this as the default provider.
        """
        self._embedding_providers[name] = provider
        if set_default or self._default_embedding is None:
            self._default_embedding = name
        logger.info("Registered embedding provider", extra={"provider": name})

    def get_llm(self, name: str | None = None) -> LLMProvider:
        """Retrieve an LLM provider by name (or the default).

        Args:
            name: Provider name, or ``None`` to use the default.

        Returns:
            The requested :class:`LLMProvider`.

        Raises:
            KeyError: If the named or default provider is not registered.
        """
        key = name or self._default_llm
        if key is None or key not in self._llm_providers:
            raise KeyError(f"LLM provider {key!r} is not registered.")
        return self._llm_providers[key]

    def get_embedding(self, name: str | None = None) -> EmbeddingProvider:
        """Retrieve an embedding provider by name (or the default).

        Args:
            name: Provider name, or ``None`` to use the default.

        Returns:
            The requested :class:`EmbeddingProvider`.

        Raises:
            KeyError: If the named or default provider is not registered.
        """
        key = name or self._default_embedding
        if key is None or key not in self._embedding_providers:
            raise KeyError(f"Embedding provider {key!r} is not registered.")
        return self._embedding_providers[key]

    @property
    def llm_names(self) -> list[str]:
        """Sorted list of registered LLM provider names.

        Returns:
            List of provider name strings.
        """
        return sorted(self._llm_providers)

    @property
    def embedding_names(self) -> list[str]:
        """Sorted list of registered embedding provider names.

        Returns:
            List of provider name strings.
        """
        return sorted(self._embedding_providers)

    def __repr__(self) -> str:
        """Return developer-friendly representation.

        Returns:
            String with LLM and embedding provider counts.
        """
        return (
            f"<ProviderRegistry llm={self.llm_names} "
            f"embedding={self.embedding_names}>"
        )

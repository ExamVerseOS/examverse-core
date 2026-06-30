"""Tests for ProviderRegistry."""

from __future__ import annotations

from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest

from examverse_core.ai.interfaces import (
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelCapabilities,
)
from examverse_core.ai.registry import ProviderRegistry


def make_llm_provider(name: str) -> LLMProvider:
    provider = MagicMock(spec=LLMProvider)
    provider.provider_name = name
    provider.complete = AsyncMock(
        return_value=LLMResponse(content="ok", model=name)
    )
    return provider  # type: ignore[return-value]


def make_embedding_provider(name: str) -> EmbeddingProvider:
    provider = MagicMock(spec=EmbeddingProvider)
    provider.provider_name = name
    return provider  # type: ignore[return-value]


class TestProviderRegistry:
    def test_register_and_get_llm(self) -> None:
        reg = ProviderRegistry()
        p = make_llm_provider("openai")
        reg.register_llm("openai", p)
        assert reg.get_llm("openai") is p

    def test_default_llm(self) -> None:
        reg = ProviderRegistry()
        p = make_llm_provider("openai")
        reg.register_llm("openai", p, set_default=True)
        assert reg.get_llm() is p

    def test_first_registered_becomes_default(self) -> None:
        reg = ProviderRegistry()
        p = make_llm_provider("openai")
        reg.register_llm("openai", p)
        assert reg.get_llm() is p

    def test_missing_llm_raises(self) -> None:
        reg = ProviderRegistry()
        with pytest.raises(KeyError):
            reg.get_llm("nonexistent")

    def test_register_and_get_embedding(self) -> None:
        reg = ProviderRegistry()
        p = make_embedding_provider("openai")
        reg.register_embedding("openai", p)
        assert reg.get_embedding("openai") is p

    def test_llm_names(self) -> None:
        reg = ProviderRegistry()
        reg.register_llm("a", make_llm_provider("a"))
        reg.register_llm("b", make_llm_provider("b"))
        assert sorted(reg.llm_names) == ["a", "b"]

    def test_repr(self) -> None:
        reg = ProviderRegistry()
        reg.register_llm("openai", make_llm_provider("openai"))
        assert "openai" in repr(reg)

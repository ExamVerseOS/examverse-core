"""Tests for generic Registry."""

from __future__ import annotations

import pytest

from examverse_core.registry.base import DuplicateKeyError, Registry


class TestRegistry:
    def test_register_and_get(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("key", 42)
        assert reg.get("key") == 42

    def test_duplicate_raises(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("key", 1)
        with pytest.raises(DuplicateKeyError):
            reg.register("key", 2)

    def test_overwrite_allowed(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("key", 1)
        reg.register("key", 2, overwrite=True)
        assert reg.get("key") == 2

    def test_require_missing_raises(self) -> None:
        reg: Registry[str, int] = Registry("test")
        with pytest.raises(KeyError):
            reg.require("missing")

    def test_unregister(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("k", 1)
        assert reg.unregister("k")
        assert reg.get("k") is None

    def test_unregister_missing_returns_false(self) -> None:
        reg: Registry[str, int] = Registry("test")
        assert not reg.unregister("nonexistent")

    def test_contains(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("k", 1)
        assert "k" in reg
        assert "x" not in reg

    def test_len(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("a", 1)
        reg.register("b", 2)
        assert len(reg) == 2

    def test_iter(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("a", 1)
        reg.register("b", 2)
        assert set(reg) == {"a", "b"}

    def test_clear(self) -> None:
        reg: Registry[str, int] = Registry("test")
        reg.register("k", 1)
        reg.clear()
        assert len(reg) == 0

    def test_repr(self) -> None:
        reg: Registry[str, int] = Registry("handlers")
        assert "handlers" in repr(reg)

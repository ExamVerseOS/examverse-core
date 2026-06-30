"""Tests for PluginRegistry — registration, lifecycle, dependency ordering."""

from __future__ import annotations

import pytest

from examverse_core.container.container import ServiceContainer
from examverse_core.events.bus import EventBus
from examverse_core.plugins.base import Plugin, PluginMetadata
from examverse_core.plugins.exceptions import (
    DuplicatePluginError,
    MissingPluginDependencyError,
    PluginCycleError,
    PluginInitializationError,
)
from examverse_core.plugins.registry import PluginRegistry


def make_plugin_class(
    name: str,
    requires: list[str] | None = None,
    fail_init: bool = False,
) -> type[Plugin]:
    class _P(Plugin):
        initialized: bool = False
        shut_down: bool = False

        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(name=name, version="1.0.0", requires=requires or [])

        async def initialize(self) -> None:
            if fail_init:
                raise RuntimeError("deliberate failure")
            _P.initialized = True

        async def shutdown(self) -> None:
            _P.shut_down = True

    return _P


@pytest.fixture
def reg() -> PluginRegistry:
    return PluginRegistry(container=ServiceContainer(), bus=EventBus())


class TestPluginRegistration:
    def test_register_single(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("alpha")
        reg.register(cls)
        assert "alpha" in reg.names

    def test_duplicate_raises(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("alpha")
        reg.register(cls)
        with pytest.raises(DuplicatePluginError):
            reg.register(cls)

    def test_len(self, reg: PluginRegistry) -> None:
        reg.register(make_plugin_class("a"))
        reg.register(make_plugin_class("b"))
        assert len(reg) == 2

    def test_get_returns_instance(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("alpha")
        reg.register(cls)
        assert reg.get("alpha") is not None

    def test_get_missing_returns_none(self, reg: PluginRegistry) -> None:
        assert reg.get("nonexistent") is None

    def test_metadata_for(self, reg: PluginRegistry) -> None:
        reg.register(make_plugin_class("alpha"))
        meta = reg.metadata_for("alpha")
        assert meta is not None
        assert meta.name == "alpha"

    def test_all_iterates(self, reg: PluginRegistry) -> None:
        reg.register(make_plugin_class("a"))
        reg.register(make_plugin_class("b"))
        names = {p.metadata.name for p in reg.all()}
        assert names == {"a", "b"}


class TestPluginLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_all(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("alpha")
        cls.initialized = False
        reg.register(cls)
        await reg.initialize_all()
        assert reg.is_initialized

    @pytest.mark.asyncio
    async def test_shutdown_all(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("alpha")
        cls.shut_down = False
        reg.register(cls)
        await reg.initialize_all()
        await reg.shutdown_all()
        assert cls.shut_down

    @pytest.mark.asyncio
    async def test_failing_plugin_raises_init_error(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("bad", fail_init=True)
        reg.register(cls)
        with pytest.raises(PluginInitializationError):
            await reg.initialize_all()

    @pytest.mark.asyncio
    async def test_dependency_ordering(self) -> None:
        order: list[str] = []
        reg = PluginRegistry(container=ServiceContainer(), bus=EventBus())

        class A(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(name="a", version="1.0.0")

            async def initialize(self) -> None:
                order.append("a")

            async def shutdown(self) -> None:
                pass

        class B(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(name="b", version="1.0.0", requires=["a"])

            async def initialize(self) -> None:
                order.append("b")

            async def shutdown(self) -> None:
                pass

        reg.register(B)
        reg.register(A)
        await reg.initialize_all()
        assert order.index("a") < order.index("b")

    def test_missing_dependency_raises(self, reg: PluginRegistry) -> None:
        cls = make_plugin_class("child", requires=["nonexistent"])
        reg.register(cls)
        with pytest.raises(MissingPluginDependencyError):
            _ = reg._topological_order()

    def test_cycle_raises(self) -> None:
        reg = PluginRegistry(container=ServiceContainer(), bus=EventBus())

        class X(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(name="x", version="1.0.0", requires=["y"])

            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

        class Y(Plugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(name="y", version="1.0.0", requires=["x"])

            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

        reg.register(X)
        reg.register(Y)
        with pytest.raises(PluginCycleError):
            reg._topological_order()

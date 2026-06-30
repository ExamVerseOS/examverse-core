"""Tests for ServiceContainer — all lifetime strategies."""

from __future__ import annotations

import pytest

from examverse_core.container.container import ServiceContainer
from examverse_core.container.exceptions import (
    CircularDependencyError,
    ScopeError,
    ServiceNotFoundError,
)


class IFoo:
    pass


class FooImpl(IFoo):
    pass


class IBar:
    pass


class BarImpl(IBar):
    def __init__(self, foo: IFoo) -> None:
        self.foo = foo


class TestSingleton:
    def test_resolves_same_instance(self) -> None:
        c = ServiceContainer()
        c.bind_singleton(IFoo, FooImpl)
        a = c.resolve(IFoo)
        b = c.resolve(IFoo)
        assert a is b

    def test_bind_instance(self) -> None:
        c = ServiceContainer()
        instance = FooImpl()
        c.bind_instance(IFoo, instance)
        resolved = c.resolve(IFoo)
        assert resolved is instance


class TestTransient:
    def test_resolves_new_instances(self) -> None:
        c = ServiceContainer()
        c.bind_transient(IFoo, FooImpl)
        a = c.resolve(IFoo)
        b = c.resolve(IFoo)
        assert a is not b


class TestScoped:
    def test_resolves_same_instance_within_scope(self) -> None:
        c = ServiceContainer()
        c.bind_scoped(IFoo, FooImpl)
        with c.scope():
            a = c.resolve(IFoo)
            b = c.resolve(IFoo)
        assert a is b

    def test_different_scopes_give_different_instances(self) -> None:
        c = ServiceContainer()
        c.bind_scoped(IFoo, FooImpl)
        with c.scope():
            a = c.resolve(IFoo)
        with c.scope():
            b = c.resolve(IFoo)
        assert a is not b

    def test_raises_outside_scope(self) -> None:
        c = ServiceContainer()
        c.bind_scoped(IFoo, FooImpl)
        with pytest.raises(ScopeError):
            c.resolve(IFoo)


class TestFactory:
    def test_factory_called_each_time(self) -> None:
        c = ServiceContainer()
        calls: list[int] = []

        def factory(container: ServiceContainer) -> FooImpl:
            calls.append(1)
            return FooImpl()

        c.bind_factory(IFoo, factory)
        c.resolve(IFoo)
        c.resolve(IFoo)
        assert len(calls) == 2


class TestAutoWiring:
    def test_auto_wires_dependency(self) -> None:
        c = ServiceContainer()
        c.bind_singleton(IFoo, FooImpl)
        c.bind_singleton(IBar, BarImpl)
        bar = c.resolve(IBar)
        assert isinstance(bar, BarImpl)
        assert isinstance(bar.foo, FooImpl)


class TestErrors:
    def test_not_found_raises(self) -> None:
        c = ServiceContainer()
        with pytest.raises(ServiceNotFoundError):
            c.resolve(IFoo)

    def test_is_registered(self) -> None:
        c = ServiceContainer()
        c.bind_singleton(IFoo, FooImpl)
        assert c.is_registered(IFoo)
        assert not c.is_registered(IBar)

    def test_clear_removes_all(self) -> None:
        c = ServiceContainer()
        c.bind_singleton(IFoo, FooImpl)
        c.clear()
        assert not c.is_registered(IFoo)

    def test_repr(self) -> None:
        c = ServiceContainer()
        c.bind_singleton(IFoo, FooImpl)
        assert "1" in repr(c)

"""Tests for identifier generation utilities."""

from __future__ import annotations

from examverse_core.utils.identifiers import (
    content_hash,
    generate_correlation_id,
    generate_id,
    generate_namespaced_id,
    generate_short_id,
)


class TestGenerateId:
    def test_uuid_format(self) -> None:
        uid = generate_id()
        assert len(uid) == 36
        assert uid.count("-") == 4

    def test_unique(self) -> None:
        assert generate_id() != generate_id()


class TestShortId:
    def test_default_length(self) -> None:
        sid = generate_short_id()
        assert len(sid) == 8

    def test_custom_length(self) -> None:
        sid = generate_short_id(length=12)
        assert len(sid) == 12

    def test_min_length_clamp(self) -> None:
        sid = generate_short_id(length=1)
        assert len(sid) == 4


class TestNamespacedId:
    def test_deterministic(self) -> None:
        a = generate_namespaced_id("exam", "JEE_2024")
        b = generate_namespaced_id("exam", "JEE_2024")
        assert a == b

    def test_different_names(self) -> None:
        a = generate_namespaced_id("exam", "JEE_2024")
        b = generate_namespaced_id("exam", "NEET_2024")
        assert a != b


class TestContentHash:
    def test_consistent(self) -> None:
        assert content_hash("hello") == content_hash("hello")

    def test_different_inputs(self) -> None:
        assert content_hash("hello") != content_hash("world")

    def test_length(self) -> None:
        assert len(content_hash("test")) == 64

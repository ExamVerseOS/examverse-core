"""Tests for JSON serialization utilities."""

from __future__ import annotations

from datetime import datetime, timezone

from examverse_core.utils.serialization import from_json, model_to_json, to_json, to_json_str


class TestToJson:
    def test_basic_dict(self) -> None:
        result = to_json({"key": "value"})
        assert b'"key"' in result

    def test_datetime_serialized(self) -> None:
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        result = to_json({"ts": dt})
        assert b"2024" in result

    def test_indent(self) -> None:
        result = to_json({"k": "v"}, indent=True)
        assert b"\n" in result


class TestFromJson:
    def test_parses_bytes(self) -> None:
        data = from_json(b'{"key": "value"}')
        assert data["key"] == "value"

    def test_parses_string(self) -> None:
        data = from_json('{"n": 42}')
        assert data["n"] == 42


class TestToJsonStr:
    def test_returns_string(self) -> None:
        result = to_json_str({"k": "v"})
        assert isinstance(result, str)

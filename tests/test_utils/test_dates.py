"""Tests for date and time utilities."""

from __future__ import annotations

from datetime import datetime, timezone

from examverse_core.utils.dates import (
    add_days,
    add_minutes,
    days_until,
    format_iso,
    human_readable_duration,
    parse_iso,
    to_utc,
    utcnow,
)


class TestUtcNow:
    def test_returns_aware_datetime(self) -> None:
        dt = utcnow()
        assert dt.tzinfo is not None
        assert dt.tzinfo == timezone.utc


class TestToUtc:
    def test_naive_datetime_assumed_utc(self) -> None:
        naive = datetime(2024, 1, 1, 12, 0, 0)
        result = to_utc(naive)
        assert result.tzinfo == timezone.utc

    def test_aware_datetime_converted(self) -> None:
        from datetime import timezone as tz
        import datetime as dt_module
        aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz.utc)
        result = to_utc(aware)
        assert result.tzinfo == timezone.utc


class TestFormatAndParse:
    def test_format_iso(self) -> None:
        dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = format_iso(dt)
        assert result.endswith("Z")
        assert "2024-06-01" in result

    def test_parse_iso_with_z(self) -> None:
        dt = parse_iso("2024-06-01T12:00:00Z")
        assert dt.tzinfo == timezone.utc
        assert dt.year == 2024


class TestAddOperations:
    def test_add_days(self) -> None:
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        result = add_days(base, 10)
        assert result.day == 11

    def test_add_minutes(self) -> None:
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = add_minutes(base, 90)
        assert result.hour == 13
        assert result.minute == 30


class TestHumanReadableDuration:
    def test_seconds_only(self) -> None:
        assert human_readable_duration(45) == "45s"

    def test_minutes_and_seconds(self) -> None:
        assert human_readable_duration(125) == "2m 5s"

    def test_hours_minutes(self) -> None:
        assert human_readable_duration(3661) == "1h 1m 1s"

    def test_zero(self) -> None:
        assert human_readable_duration(0) == "0s"

    def test_negative_returns_zero(self) -> None:
        assert human_readable_duration(-10) == "0s"

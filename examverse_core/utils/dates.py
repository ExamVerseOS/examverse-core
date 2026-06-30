"""Date and time utilities for ExamVerseOS.

Example:
    >>> utcnow()
    datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import overload


def utcnow() -> datetime:
    """Return the current UTC datetime with timezone info.

    Returns:
        Timezone-aware UTC :class:`datetime`.
    """
    return datetime.now(tz=timezone.utc)


def utc_date() -> date:
    """Return the current UTC date.

    Returns:
        Today's UTC :class:`date`.
    """
    return datetime.now(tz=timezone.utc).date()


def to_utc(dt: datetime) -> datetime:
    """Convert a naive or aware datetime to UTC.

    Naive datetimes are assumed to be in UTC.

    Args:
        dt: The datetime to convert.

    Returns:
        A UTC timezone-aware :class:`datetime`.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def days_until(target: date | datetime) -> int:
    """Return the number of days from today (UTC) until the target date.

    Args:
        target: A future (or past) date or datetime.

    Returns:
        Integer day count (negative if in the past).
    """
    today = utc_date()
    if isinstance(target, datetime):
        target = to_utc(target).date()
    return (target - today).days


def add_days(dt: datetime, days: int) -> datetime:
    """Add (or subtract) a number of days to a datetime.

    Args:
        dt: The base datetime.
        days: Number of days to add (use negative to subtract).

    Returns:
        A new :class:`datetime` offset by ``days``.
    """
    return dt + timedelta(days=days)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """Add (or subtract) a number of minutes to a datetime.

    Args:
        dt: The base datetime.
        minutes: Number of minutes to add.

    Returns:
        A new :class:`datetime` offset by ``minutes``.
    """
    return dt + timedelta(minutes=minutes)


def format_iso(dt: datetime) -> str:
    """Format a datetime as an ISO 8601 string with UTC suffix.

    Args:
        dt: The datetime to format.

    Returns:
        ISO 8601 string ending in ``Z``.
    """
    return to_utc(dt).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@overload
def parse_iso(value: str) -> datetime: ...


def parse_iso(value: str) -> datetime:
    """Parse an ISO 8601 datetime string into a UTC-aware datetime.

    Args:
        value: An ISO 8601 string (with or without timezone info).

    Returns:
        A UTC-aware :class:`datetime`.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return to_utc(dt)


def human_readable_duration(seconds: int) -> str:
    """Convert seconds into a human-readable duration string.

    Args:
        seconds: Non-negative integer seconds.

    Returns:
        A string like ``"2h 15m"`` or ``"45s"``.
    """
    if seconds < 0:
        return "0s"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)

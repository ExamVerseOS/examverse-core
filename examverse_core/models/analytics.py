"""Analytics and settings domain models for ExamVerseOS."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from examverse_core.models.base import BaseEntity


class AnalyticsEvent(BaseEntity):
    """A single tracked user interaction or system event.

    Attributes:
        user_id: The user who triggered the event (``None`` for anonymous).
        session_id: Browser / app session identifier.
        event_name: Dot-namespaced event name (e.g. ``"question.answered"``).
        properties: Arbitrary event properties.
        device_type: ``"mobile"``, ``"desktop"``, or ``"tablet"``.
        platform: ``"web"``, ``"ios"``, or ``"android"``.
        app_version: Application version string.
        ip_address: Optional client IP (should be anonymised before storage).
    """

    user_id: str | None = None
    session_id: str | None = None
    event_name: str = Field(..., min_length=1, max_length=200)
    properties: dict[str, Any] = Field(default_factory=dict)
    device_type: str | None = Field(default=None, max_length=20)
    platform: str | None = Field(default=None, max_length=20)
    app_version: str | None = Field(default=None, max_length=30)
    ip_address: str | None = None


class Settings(BaseEntity):
    """Key-value settings record scoped to a user, tenant, or the system.

    Attributes:
        scope: Scope identifier (e.g. ``"system"``, ``"user:<id>"``, ``"tenant:<id>"``).
        key: Dot-namespaced setting key.
        value: The setting value (any JSON-serialisable type).
        description: Human-readable description.
        is_secret: Whether the value should be masked in logs/API responses.
    """

    scope: str = Field(..., min_length=1, max_length=100)
    key: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-z][a-z0-9_.]*$")
    value: Any
    description: str | None = Field(default=None, max_length=500)
    is_secret: bool = False

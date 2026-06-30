"""Base event classes for the ExamVerse event-driven architecture.

All domain events in the ExamVerseOS ecosystem extend :class:`DomainEvent`.
Events are immutable value objects identified by a unique ID and a timestamp.

Example:
    >>> from examverse_core.events.base import DomainEvent
    >>> class UserCreated(DomainEvent):
    ...     user_id: str
    ...     email: str
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Immutable base class for all domain events.

    Attributes:
        event_id: Unique identifier for this event instance.
        event_type: Dotted-path name used for routing (auto-derived from class name).
        occurred_at: UTC timestamp when this event was created.
        correlation_id: Optional tracing token that links related events.
        metadata: Arbitrary key-value pairs for headers, tracing, etc.
        version: Schema version; increment when the payload shape changes.
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event instance identifier",
    )
    event_type: str = Field(default="", description="Fully-qualified event type name")
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC creation timestamp",
    )
    correlation_id: str | None = Field(
        default=None,
        description="Links related events in a distributed trace",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary headers and tracing metadata",
    )
    version: int = Field(default=1, ge=1, description="Event schema version")

    _event_type_override: ClassVar[str | None] = None

    model_config = {"frozen": True}

    def model_post_init(self, __context: Any) -> None:
        """Populate ``event_type`` from the class name if not set.

        Args:
            __context: Pydantic internal context (unused).
        """
        if not self.event_type:
            override = self.__class__._event_type_override
            name = override or self.__class__.__name__
            object.__setattr__(self, "event_type", name)

    @classmethod
    def event_name(cls) -> str:
        """Return the canonical event type name for this class.

        Returns:
            The event type string used for subscription matching.
        """
        return cls._event_type_override or cls.__name__


class ExamVerseEvent(DomainEvent):
    """Marker base for all first-party ExamVerse domain events.

    Third-party plugins may extend :class:`DomainEvent` directly; first-party
    repositories should extend this class to signal provenance.
    """

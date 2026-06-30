"""Base model classes shared across the entire ExamVerseOS domain.

All domain models extend :class:`BaseEntity` which provides standard
audit fields (id, created_at, updated_at) and immutability guarantees.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    """Return the current UTC datetime.

    Returns:
        Timezone-aware UTC datetime.
    """
    return datetime.now(tz=timezone.utc)


class BaseEntity(BaseModel):
    """Root base class for all ExamVerse domain entities.

    Attributes:
        id: Globally unique entity identifier (UUID v4).
        created_at: UTC timestamp of creation.
        updated_at: UTC timestamp of last modification.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Entity ID")
    created_at: datetime = Field(default_factory=_utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=_utcnow, description="Last update timestamp")

    model_config = {"from_attributes": True}

    def model_with_updates(self, **changes: Any) -> BaseEntity:
        """Return a new instance with the given fields changed.

        The ``updated_at`` field is automatically refreshed to now.

        Args:
            **changes: Fields to update.

        Returns:
            A new entity instance with the applied changes.
        """
        return self.model_copy(update={**changes, "updated_at": _utcnow()})


class BaseValueObject(BaseModel):
    """Root base class for immutable domain value objects.

    Value objects have no identity — they are equal when all their
    fields are equal.
    """

    model_config = {"frozen": True}


class BaseReadModel(BaseModel):
    """Base class for read-only query projections (CQRS read side).

    Read models are flat, denormalised, and optimised for display.
    They are not persisted; they are produced by query handlers.
    """

    model_config = {"frozen": True, "from_attributes": True}

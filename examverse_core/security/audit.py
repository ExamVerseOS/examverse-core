"""Audit log model and writer for ExamVerseOS security events."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """An immutable record of a security-relevant action.

    Attributes:
        id: Unique audit record identifier.
        user_id: The acting user (``None`` for system actions).
        action: Dot-namespaced action name (e.g. ``"user.login"``).
        resource_type: Type of the resource affected (e.g. ``"Exam"``).
        resource_id: Identifier of the specific resource.
        outcome: ``"success"`` or ``"failure"``.
        ip_address: Client IP address (anonymised if required).
        user_agent: Client user-agent string.
        metadata: Arbitrary structured details for the action.
        occurred_at: UTC timestamp of the event.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    action: str = Field(..., min_length=1, max_length=200)
    resource_type: str | None = Field(default=None, max_length=100)
    resource_id: str | None = None
    outcome: str = Field(default="success", pattern=r"^(success|failure)$")
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    model_config = {"frozen": True}


class AuditWriter:
    """Interface for persisting audit entries.

    Downstream services implement this interface and register it with the
    DI container. Core code depends only on this class.
    """

    async def write(self, entry: AuditEntry) -> None:
        """Persist a single audit entry.

        Args:
            entry: The :class:`AuditEntry` to persist.
        """

    def build_entry(
        self,
        action: str,
        *,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        outcome: str = "success",
        ip_address: str | None = None,
        user_agent: str | None = None,
        **metadata: Any,
    ) -> AuditEntry:
        """Construct an :class:`AuditEntry` from keyword arguments.

        Args:
            action: The action name (e.g. ``"exam.published"``).
            user_id: The acting user identifier.
            resource_type: The type of affected resource.
            resource_id: The affected resource identifier.
            outcome: ``"success"`` or ``"failure"``.
            ip_address: Client IP address.
            user_agent: Client user-agent string.
            **metadata: Additional structured metadata.

        Returns:
            A frozen :class:`AuditEntry` ready for persistence.
        """
        return AuditEntry(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

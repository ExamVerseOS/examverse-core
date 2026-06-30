"""AI-related domain models — conversations, messages, requests, and responses."""

from __future__ import annotations

import enum
from typing import Any

from pydantic import Field

from examverse_core.models.base import BaseEntity


class ConversationStatus(str, enum.Enum):
    """Lifecycle states for an AI conversation."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(str, enum.Enum):
    """Speaker roles in an AI conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Conversation(BaseEntity):
    """An AI-assisted conversation session.

    Attributes:
        user_id: The user who owns this conversation.
        title: Auto-generated or user-defined conversation title.
        status: Current lifecycle state.
        provider: The AI provider used (e.g. ``"openai"``).
        model: The specific model used.
        system_prompt: System-level instructions for this conversation.
        context_metadata: Arbitrary context (subject, topic, exam, etc.).
        total_input_tokens: Cumulative input token usage.
        total_output_tokens: Cumulative output token usage.
    """

    user_id: str
    title: str = Field(..., min_length=1, max_length=300)
    status: ConversationStatus = ConversationStatus.ACTIVE
    provider: str = Field(..., max_length=50)
    model: str = Field(..., max_length=100)
    system_prompt: str | None = Field(default=None, max_length=10000)
    context_metadata: dict[str, Any] = Field(default_factory=dict)
    total_input_tokens: int = Field(default=0, ge=0)
    total_output_tokens: int = Field(default=0, ge=0)


class ConversationMessage(BaseEntity):
    """A single message turn in an AI conversation.

    Attributes:
        conversation_id: Parent conversation identifier.
        role: Speaker role.
        content: Message text content.
        input_tokens: Tokens consumed by this message.
        output_tokens: Tokens generated in this message.
        latency_ms: Time taken to generate the response in milliseconds.
        metadata: Arbitrary metadata (tool calls, citations, etc.).
    """

    conversation_id: str
    role: MessageRole
    content: str = Field(..., min_length=0, max_length=50000)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIRequest(BaseEntity):
    """Persisted record of an AI API request for auditing and billing.

    Attributes:
        user_id: Requesting user.
        conversation_id: Associated conversation (if applicable).
        provider: AI provider name.
        model: Model identifier.
        operation: Type of operation (``"completion"``, ``"embedding"``, etc.).
        input_tokens: Tokens in the request.
        output_tokens: Tokens in the response.
        cost_usd: Estimated cost in US dollars.
        latency_ms: Total round-trip latency in milliseconds.
        status: Request status (``"success"`` / ``"error"``).
        error_message: Error detail if status is ``"error"``.
    """

    user_id: str
    conversation_id: str | None = None
    provider: str = Field(..., max_length=50)
    model: str = Field(..., max_length=100)
    operation: str = Field(..., max_length=50)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    latency_ms: int = Field(default=0, ge=0)
    status: str = Field(default="success", max_length=20)
    error_message: str | None = None


class Notification(BaseEntity):
    """A notification sent to a user.

    Attributes:
        user_id: Recipient user identifier.
        title: Notification title.
        body: Notification body text.
        type: Notification category (e.g. ``"reminder"``, ``"achievement"``).
        channel: Delivery channel (``"push"``, ``"email"``, ``"in_app"``).
        is_read: Whether the user has marked it read.
        action_url: Optional deep-link URL.
        metadata: Arbitrary payload for the notification.
    """

    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=2000)
    type: str = Field(..., max_length=50)
    channel: str = Field(default="in_app", max_length=20)
    is_read: bool = False
    action_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

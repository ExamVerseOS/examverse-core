"""AI provider interfaces for the ExamVerseOS AI abstraction layer.

No concrete AI SDK (OpenAI, Anthropic, Gemini, etc.) is imported here.
Future repositories implement these protocols and register themselves via
the :class:`ProviderRegistry`. Core code depends only on these interfaces.

Example:
    >>> class MyOpenAIProvider:
    ...     async def complete(self, request: LLMRequest) -> LLMResponse:
    ...         ...  # vendor-specific implementation
"""

from __future__ import annotations

import abc
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field


class ModelCapabilities(BaseModel):
    """Describes what a specific model version supports.

    Attributes:
        model_id: Vendor model identifier (e.g. ``"gpt-4o"``).
        max_context_tokens: Maximum token window size.
        supports_streaming: Whether the model supports token streaming.
        supports_function_calling: Whether the model supports tool/function calls.
        supports_vision: Whether the model can process image inputs.
        supports_embeddings: Whether the model produces embeddings.
        cost_per_input_token: Approximate USD cost per input token.
        cost_per_output_token: Approximate USD cost per output token.
    """

    model_id: str
    max_context_tokens: int
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_embeddings: bool = False
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0


class Message(BaseModel):
    """A single turn in a conversation.

    Attributes:
        role: One of ``"system"``, ``"user"``, ``"assistant"``, or ``"tool"``.
        content: The text content of the message.
        name: Optional name for multi-participant conversations.
    """

    role: str = Field(..., pattern=r"^(system|user|assistant|tool)$")
    content: str
    name: str | None = None


class LLMRequest(BaseModel):
    """Input payload for a language model completion.

    Attributes:
        messages: Ordered conversation history.
        model: Requested model identifier.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Maximum output tokens.
        stream: Request streaming output.
        tools: Optional tool/function definitions for function-calling models.
        metadata: Arbitrary provider-specific options.
    """

    messages: list[Message]
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = None
    stream: bool = False
    tools: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Output from a language model completion.

    Attributes:
        content: The generated text.
        model: The model that produced the response.
        input_tokens: Number of tokens in the request.
        output_tokens: Number of tokens in the response.
        finish_reason: Why generation stopped (e.g. ``"stop"``, ``"length"``).
        metadata: Arbitrary provider-specific response fields.
    """

    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    """Input payload for an embedding provider.

    Attributes:
        texts: List of strings to embed.
        model: Requested embedding model identifier.
        metadata: Arbitrary provider-specific options.
    """

    texts: list[str]
    model: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    """Output from an embedding provider.

    Attributes:
        embeddings: One float vector per input text.
        model: The model that produced the embeddings.
        total_tokens: Total tokens consumed.
    """

    embeddings: list[list[float]]
    model: str
    total_tokens: int = 0


class LLMProvider(abc.ABC):
    """Interface for language model providers.

    Concrete implementations live in downstream repositories (e.g.
    ``examverse-ai``). Core code references only this interface.
    """

    @abc.abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Perform a non-streaming completion.

        Args:
            request: The completion request payload.

        Returns:
            The completed :class:`LLMResponse`.
        """

    @abc.abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Perform a streaming completion, yielding tokens as they arrive.

        Args:
            request: The completion request payload (``stream`` must be ``True``).

        Yields:
            Individual token strings as they are generated.
        """

    @abc.abstractmethod
    def get_capabilities(self, model_id: str) -> ModelCapabilities:
        """Return the capability descriptor for a specific model.

        Args:
            model_id: The vendor model identifier.

        Returns:
            A :class:`ModelCapabilities` instance.
        """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """The unique provider identifier (e.g. ``"openai"``).

        Returns:
            Provider name string.
        """


class EmbeddingProvider(abc.ABC):
    """Interface for text embedding providers."""

    @abc.abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Produce vector embeddings for the given texts.

        Args:
            request: The embedding request payload.

        Returns:
            An :class:`EmbeddingResponse` containing one vector per text.
        """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """The unique provider identifier.

        Returns:
            Provider name string.
        """


class VectorStore(abc.ABC):
    """Interface for vector databases and similarity search backends."""

    @abc.abstractmethod
    async def upsert(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Insert or update a vector record.

        Args:
            id: Unique record identifier.
            vector: The embedding vector.
            metadata: Arbitrary metadata stored alongside the vector.
        """

    @abc.abstractmethod
    async def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Find the top-k most similar vectors to the query.

        Args:
            query_vector: The query embedding.
            top_k: Number of results to return.
            filters: Optional metadata filters.

        Returns:
            List of result dicts with ``id``, ``score``, and ``metadata`` keys.
        """

    @abc.abstractmethod
    async def delete(self, id: str) -> bool:
        """Remove a vector record by ID.

        Args:
            id: The record identifier to delete.

        Returns:
            ``True`` if the record was found and deleted.
        """


class ConversationMemory(abc.ABC):
    """Interface for conversation history storage backends."""

    @abc.abstractmethod
    async def add_message(self, conversation_id: str, message: Message) -> None:
        """Append a message to the given conversation.

        Args:
            conversation_id: The conversation to append to.
            message: The message to store.
        """

    @abc.abstractmethod
    async def get_messages(
        self, conversation_id: str, limit: int | None = None
    ) -> list[Message]:
        """Retrieve messages for a conversation.

        Args:
            conversation_id: The conversation identifier.
            limit: Maximum number of messages to return (most recent first).

        Returns:
            Ordered list of :class:`Message` objects.
        """

    @abc.abstractmethod
    async def clear(self, conversation_id: str) -> None:
        """Delete all messages for a conversation.

        Args:
            conversation_id: The conversation to clear.
        """


class PromptFormatter(abc.ABC):
    """Interface for domain-specific prompt construction utilities."""

    @abc.abstractmethod
    def format(self, template: str, **variables: Any) -> str:
        """Render a prompt template with the given variables.

        Args:
            template: The prompt template string.
            **variables: Values to substitute into the template.

        Returns:
            The rendered prompt string.
        """


class TokenCounter(abc.ABC):
    """Interface for token counting utilities."""

    @abc.abstractmethod
    def count(self, text: str, model: str) -> int:
        """Count the number of tokens in the given text for a specific model.

        Args:
            text: The text to tokenize.
            model: The model whose tokenizer to use.

        Returns:
            Token count.
        """

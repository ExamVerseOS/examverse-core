# ADR 004 — AI Provider Abstraction Layer

**Status:** Accepted  
**Date:** 2024-06-01

---

## Context

ExamVerseOS requires AI capabilities (completions, embeddings, vector search, conversation memory) from multiple providers: OpenAI, Anthropic, Gemini, DeepSeek, Groq, and potentially custom/self-hosted models (Ollama). Binding to any single vendor SDK in core would:

- Create a hard dependency on a third-party library with breaking change risk.
- Prevent swapping providers without modifying core code.
- Make it impossible to route different features to different providers.

---

## Decision

Define **provider interfaces** in `examverse_core.ai.interfaces` and a **`ProviderRegistry`** for runtime registration. No concrete AI SDK is imported anywhere in examverse-core.

Interfaces defined:
- `LLMProvider` — `complete()`, `stream()`, `get_capabilities()`
- `EmbeddingProvider` — `embed()`
- `VectorStore` — `upsert()`, `search()`, `delete()`
- `ConversationMemory` — `add_message()`, `get_messages()`, `clear()`
- `PromptFormatter` — `format()`
- `TokenCounter` — `count()`

Concrete implementations live in `examverse-ai` and are registered as plugins.

---

## Consequences

**Positive:**
- Core has zero vendor lock-in.
- Multiple providers can be registered simultaneously (e.g. OpenAI for completions, Cohere for embeddings).
- Provider swap requires only a plugin change, not a core change.
- Models and requests are vendor-agnostic Pydantic types.

**Negative:**
- The abstraction layer must be kept in sync with vendor capabilities (e.g. new parameters).
- Provider-specific features (fine-tuning, function calling schemas) require interface evolution.

---

## Interface Stability Policy

- Additive changes (new optional fields on `LLMRequest`) → minor version bump.
- Breaking changes (removing a method, changing signatures) → major version bump with deprecation notice.

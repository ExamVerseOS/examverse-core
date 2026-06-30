# ADR 003 — Async Event Bus

**Status:** Accepted  
**Date:** 2024-06-01

---

## Context

ExamVerseOS services need a way to communicate without direct coupling. When a question is answered, multiple subsystems may need to react: progress tracking, analytics, AI personalization, notifications. Hard-coding these call chains creates tight coupling and makes the system harder to extend.

---

## Decision

Implement an **in-process async event bus** (`EventBus`) that:

1. Uses **typed domain events** (Pydantic models extending `DomainEvent`) as the communication contract.
2. Supports **priority groups** — handlers with a lower priority number run before those with a higher number, in grouped concurrent batches.
3. Supports **configurable per-handler retry** with exponential back-off and jitter.
4. Provides a **composable middleware pipeline** that wraps each publish call (logging, correlation ID injection, metrics, etc.).
5. Is **in-process only** — no broker dependency. Message broker integration (Kafka, RabbitMQ) is a separate concern for downstream repositories.

---

## Consequences

**Positive:**
- Zero infrastructure dependency for in-process communication.
- Handlers for the same event can be added by any plugin without modifying the publisher.
- Middleware provides clean extension points for observability.
- Priority groups allow ordering guarantees where needed (e.g. audit before analytics).

**Negative:**
- Not persistent — events are lost if the process crashes mid-dispatch.
- Not distributed — cross-service events still require a message broker.
- Retry logic is simplistic (exponential back-off); a dead-letter queue requires broker integration.

---

## Future Work

A `BrokerEventBus` adapter in `examverse-messaging` will implement the same `EventBus` interface but publish to Kafka/RabbitMQ, enabling cross-service event flow. Core code will not need to change.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Direct method calls between services | Tight coupling; violates OCP |
| Celery tasks | Requires broker; heavyweight for in-process use |
| Python `pubsub` library | Not async-native; limited middleware support |
| `asyncio.Queue` | Low-level; no subscriber registration abstraction |

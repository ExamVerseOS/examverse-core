# ADR 002 — Dependency Injection Container

**Status:** Accepted  
**Date:** 2024-06-01

---

## Context

Services across ExamVerseOS need to depend on abstractions (interfaces) rather than concrete implementations, enabling:
- Testability (replace real dependencies with test doubles)
- Pluggability (swap implementations without changing call sites)
- Lifecycle management (singletons, per-request scoping)

A manual factory/locator pattern creates hidden coupling and makes dependency graphs hard to audit.

---

## Decision

Implement a **first-class DI container** (`ServiceContainer`) inside examverse-core with:

1. **Four lifetime strategies:** singleton, transient, scoped (async-safe via `ContextVar`), factory.
2. **Automatic constructor injection** via `inspect` + `get_type_hints` — no decorators or annotations required on the consumer side.
3. **Thread-safe singleton cache** using `threading.Lock`.
4. **Circular dependency detection** via a resolution chain passed through the recursive resolver.
5. **Scope isolation** via `contextvar` so each async request gets its own scoped instances without cross-contamination.

---

## Consequences

**Positive:**
- Consumers depend only on interfaces; concrete types are registered at the composition root (plugin `register_services()`).
- Tests can bind mock implementations trivially.
- Scoped lifetime works correctly in asyncio without thread locks on the hot path.

**Negative:**
- Auto-wiring requires type hints to be present and resolvable at import time.
- The container adds indirection that can confuse developers unfamiliar with DI.
- `get_type_hints` can fail with forward references in certain import orders.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| `dependency-injector` (third-party) | Heavy dependency; not worth for foundational library |
| `inject` / `injector` | Requires decorators on consumer classes; invasive |
| Manual service locator | Global mutable state; anti-pattern |
| Constructor-only DI (no container) | Does not support plugin-driven registration |

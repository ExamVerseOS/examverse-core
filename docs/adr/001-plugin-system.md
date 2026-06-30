# ADR 001 — Plugin System Design

**Status:** Accepted  
**Date:** 2024-06-01

---

## Context

ExamVerseOS needs to support a wide and growing range of capabilities (AI providers, search engines, payment gateways, notification channels, analytics backends, etc.) without requiring modifications to core library code each time a new capability is added.

The platform must satisfy the **Open/Closed Principle**: open for extension, closed for modification.

---

## Decision

Implement a **plugin-first architecture** where:

1. All optional capabilities are encapsulated in plugins.
2. Plugins are **auto-discovered** via Python package entry points (PEP 451 / `importlib.metadata`).
3. Each plugin implements a well-defined `Plugin` abstract base class with six lifecycle hooks.
4. Plugin dependencies are declared explicitly in `PluginMetadata.requires` and resolved via topological sort.
5. Plugins bind services into the DI container, subscribe to events, and optionally register HTTP routes — all without direct coupling to other plugins.

---

## Consequences

**Positive:**
- New capabilities enter the system without modifying existing code.
- Any installed Python package can become a plugin by adding an entry point.
- Circular dependency detection prevents ordering bugs.
- The plugin graph is introspectable at runtime.

**Negative:**
- Plugin discovery requires Python packaging (cannot be done with loose scripts).
- Topological ordering adds startup complexity.
- Plugins that share state must coordinate via the DI container and event bus — no direct references.

---

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Manual plugin registration in a config file | Requires code changes per plugin addition |
| Subclass scanning (walk all `Plugin` subclasses) | Brittle; requires importing every module upfront |
| Dynamic import by string path only | No auto-discovery; still requires configuration changes |

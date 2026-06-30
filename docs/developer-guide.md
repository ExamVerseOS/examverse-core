# Developer Guide — examverse-core

## Getting Started

### Requirements

- Python 3.12+
- Poetry 1.8+

### Setup

```bash
# Clone and install
git clone https://github.com/examverse/examverse-core.git
cd examverse-core
poetry install

# Verify everything passes
poetry run pytest
poetry run mypy examverse_core
poetry run ruff check examverse_core tests
```

---

## Project Layout

```
examverse-core/
├── examverse_core/          # Main package
│   ├── __init__.py          # Public API surface
│   ├── plugins/             # Plugin framework
│   │   ├── base.py          # Plugin ABC + PluginMetadata
│   │   ├── registry.py      # PluginRegistry
│   │   └── exceptions.py    # Plugin-related exceptions
│   ├── container/           # Dependency injection
│   │   ├── container.py     # ServiceContainer
│   │   ├── descriptors.py   # Lifetime descriptors
│   │   ├── resolver.py      # Auto-wiring resolver
│   │   └── exceptions.py    # DI exceptions
│   ├── events/              # Event bus
│   │   ├── base.py          # DomainEvent base class
│   │   ├── bus.py           # EventBus
│   │   └── middleware.py    # Event middleware
│   ├── ai/                  # AI abstractions
│   │   ├── interfaces.py    # LLMProvider, EmbeddingProvider, …
│   │   └── registry.py      # ProviderRegistry
│   ├── models/              # Domain models
│   │   ├── base.py          # BaseEntity, BaseValueObject, BaseReadModel
│   │   ├── user.py          # User, UserRole, UserStatus
│   │   ├── exam.py          # Exam, Subject, Topic, Question, PYQ, Book
│   │   ├── study.py         # StudySession, Flashcard, Progress, …
│   │   ├── ai.py            # Conversation, AIRequest, Notification
│   │   └── analytics.py     # AnalyticsEvent, Settings
│   ├── config/              # Typed configuration
│   │   └── settings.py      # CoreSettings + sub-settings
│   ├── logging/             # Structured logging
│   │   ├── logger.py        # configure_logging, get_logger
│   │   └── context.py       # Correlation/trace ID context vars
│   ├── security/            # Security utilities
│   │   ├── jwt.py           # JWTHelper
│   │   ├── permissions.py   # PermissionChecker, Permission
│   │   ├── audit.py         # AuditEntry, AuditWriter
│   │   ├── crypto.py        # PasswordHasher, SymmetricEncryption
│   │   └── exceptions.py    # Security exceptions
│   ├── validation/          # Domain validators
│   │   └── validators.py    # email, slug, uuid, url, filename, phone
│   ├── utils/               # General utilities
│   │   ├── pagination.py    # Page, PaginationParams, paginate()
│   │   ├── retry.py         # @retry, retry_call()
│   │   ├── dates.py         # utcnow, format_iso, parse_iso, …
│   │   ├── hashing.py       # sha256_hex, hmac_sha256_hex, …
│   │   ├── compression.py   # compress, decompress (zstd)
│   │   ├── reflection.py    # import_class, get_subclasses, …
│   │   ├── identifiers.py   # generate_id, generate_short_id, …
│   │   └── serialization.py # to_json, from_json, model_to_json
│   └── registry/            # Generic registry
│       └── base.py          # Registry[K, V]
├── tests/                   # Full test suite
├── docs/                    # Documentation
└── pyproject.toml           # Package manifest
```

---

## Running Tests

```bash
# Full test run with coverage report
poetry run pytest

# Fast run (no coverage)
poetry run pytest --no-cov

# Single module
poetry run pytest tests/test_plugins/

# Specific test
poetry run pytest tests/test_events/test_bus.py::TestRetries
```

Coverage target: **≥ 90%**.

---

## Type Checking

```bash
poetry run mypy examverse_core
```

The project is configured with `strict = true`. All code must be fully annotated.

---

## Linting and Formatting

```bash
# Check
poetry run ruff check examverse_core tests

# Fix
poetry run ruff check --fix examverse_core tests

# Format
poetry run black examverse_core tests

# Check format without writing
poetry run black --check examverse_core tests
```

---

## Adding a New Module

1. Create `examverse_core/<module>/` directory.
2. Add `__init__.py` that re-exports the public API.
3. Write the implementation in named files.
4. Add tests in `tests/test_<module>/`.
5. Export the new module from `examverse_core/__init__.py` if it's a top-level concern.
6. Update `docs/architecture.md` with the new module's role.

---

## Adding a New Domain Model

1. Identify which file it belongs to (`user.py`, `exam.py`, `study.py`, `ai.py`, `analytics.py`).
2. Extend `BaseEntity` for mutable entities with an identity.
3. Extend `BaseValueObject` for immutable value objects.
4. Extend `BaseReadModel` for CQRS read projections.
5. Add the model to the module's `__init__.py` `__all__` list.
6. Add a test in `tests/test_models/test_models.py`.

---

## Coding Standards

- **100% type hints** — every function parameter, return value, and class attribute.
- **Google docstrings** — all public classes, methods, and module-level functions.
- **No TODOs** — finish or open a ticket.
- **No placeholders** — no `pass` in implementations, no `...` bodies in non-abstract methods.
- **No mock implementations** — real logic only; stubs live in tests.
- **Explicit errors** — raise named exceptions, never swallow silently.
- **Immutability** — domain events and value objects use `model_config = {"frozen": True}`.

---

## Versioning

examverse-core follows **Semantic Versioning** (semver):

- `PATCH` — bug fixes, non-breaking internal changes.
- `MINOR` — new backwards-compatible features.
- `MAJOR` — breaking changes to public interfaces.

All downstream services pin a compatible minor version: `examverse-core = "^0.1"`.

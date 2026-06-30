# examverse-core

The shared runtime foundation for the **ExamVerseOS** ecosystem.

Every backend service in the ExamVerse platform — `examverse-api`, `examverse-ai`, `examverse-db`, `examverse-ingestion`, `examverse-sdk`, and more — depends on this library. It supplies the foundational building blocks that all services share, without implementing any business logic itself.

---

## Why examverse-core?

| Without core | With core |
|---|---|
| Each service reimplements DI, events, logging, auth helpers, models | One canonical implementation, consumed everywhere |
| Breaking changes cascade unpredictably | Versioned, tested contracts |
| Adding new capabilities requires modifying existing code | Add a plugin; existing code is untouched |

---

## Architecture at a Glance

```
examverse_core/
├── plugins/        # Plugin system — auto-discovery, lifecycle, DI
├── container/      # Dependency injection — singleton, transient, scoped, factory
├── events/         # Async event bus — publish/subscribe, middleware, priorities
├── ai/             # AI abstraction — LLMProvider, EmbeddingProvider, VectorStore
├── models/         # Shared Pydantic domain models (User, Exam, Question, …)
├── config/         # Typed configuration via pydantic-settings
├── logging/        # Structured JSON logging + correlation IDs
├── security/       # JWT helpers, permissions, audit, crypto
├── validation/     # Reusable domain validators
├── utils/          # Pagination, retry, dates, hashing, serialization, …
└── registry/       # Generic thread-safe registry
```

---

## Quick Start

```python
from examverse_core import ServiceContainer, EventBus, PluginRegistry
from examverse_core.config import CoreSettings
from examverse_core.logging import configure_logging, get_logger

# 1. Configure logging
settings = CoreSettings()
configure_logging(service_name=settings.service_name, log_level=settings.log_level)
log = get_logger(__name__)

# 2. Build the DI container
container = ServiceContainer()
container.bind_singleton(IMyService, MyServiceImpl)

# 3. Build the event bus
bus = EventBus()

# 4. Load and start plugins
registry = PluginRegistry(container=container, bus=bus)
registry.load_from_entry_points(group="examverse.plugins")
await registry.initialize_all()

# ... application runs ...

await registry.shutdown_all()
```

---

## Plugin System

New functionality is added as **plugins** — no modifications to existing source code required.

```python
from examverse_core.plugins import Plugin, PluginMetadata

class SearchPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="search",
            version="1.0.0",
            description="Full-text search powered by OpenSearch",
        )

    def register_services(self) -> None:
        self._container.bind_singleton(ISearchService, OpenSearchService)

    def register_events(self) -> None:
        self._bus.subscribe(QuestionCreated, self._index_question)

    async def initialize(self) -> None:
        svc = self._container.resolve(ISearchService)
        await svc.ping()

    async def shutdown(self) -> None:
        svc = self._container.resolve(ISearchService)
        await svc.close()
```

**Auto-discovery via entry points:**

```toml
# pyproject.toml of examverse-search
[tool.poetry.plugins."examverse.plugins"]
search = "examverse_search.plugin:SearchPlugin"
```

---

## Dependency Injection

```python
container = ServiceContainer()

# Bind by interface → implementation
container.bind_singleton(ICache, RedisCache)
container.bind_transient(IUnitOfWork, SqlAlchemyUnitOfWork)
container.bind_scoped(IRequestContext, RequestContext)
container.bind_factory(IReportBuilder, lambda c: ReportBuilder(c.resolve(ICache)))

# Resolve (constructor args are auto-injected via type hints)
cache = container.resolve(ICache)

# Scoped lifetime
with container.scope():
    uow = container.resolve(IUnitOfWork)  # same instance within the scope
```

---

## Event Bus

```python
from examverse_core.events import EventBus, DomainEvent

class QuestionAnswered(DomainEvent):
    user_id: str
    question_id: str
    is_correct: bool

bus = EventBus()

@bus.subscribe(QuestionAnswered, priority=10, max_retries=3)
async def update_progress(event: QuestionAnswered) -> None:
    ...

await bus.publish(QuestionAnswered(
    user_id="u1", question_id="q1", is_correct=True
))
```

---

## AI Abstractions

```python
from examverse_core.ai import LLMProvider, LLMRequest, ProviderRegistry

registry = ProviderRegistry()
registry.register_llm("openai", my_openai_impl, set_default=True)

provider = registry.get_llm()
response = await provider.complete(LLMRequest(
    messages=[{"role": "user", "content": "Explain Newton's first law."}],
    model="gpt-4o",
))
```

No concrete AI SDK is imported in core. Provider implementations live in `examverse-ai`.

---

## Domain Models

```python
from examverse_core.models import User, Exam, Question, StudySession, Flashcard

user = User(
    email="student@example.com",
    username="rahul",
    full_name="Rahul Sharma",
    hashed_password="...",
)
```

---

## Security Utilities

```python
from examverse_core.security import (
    JWTHelper, PasswordHasher, SymmetricEncryption,
    PermissionChecker, Permission
)
from examverse_core.models.user import UserRole

# JWT
helper = JWTHelper(secret="...", access_expire_minutes=30)
token = helper.create_access_token({"sub": user.id})
payload = helper.decode(token)

# Password hashing
hasher = PasswordHasher()
hashed = hasher.hash("my-password")
hasher.verify("my-password", hashed)  # True

# Permission check
checker = PermissionChecker()
checker.has_permission(UserRole.TEACHER, Permission.CREATE_EXAM)  # True
```

---

## Installation

```bash
# With Poetry
poetry add examverse-core

# Direct pip (from internal registry)
pip install examverse-core
```

---

## Development

```bash
# Install all dependencies
poetry install

# Run tests with coverage
poetry run pytest

# Type-check
poetry run mypy examverse_core

# Lint + format
poetry run ruff check examverse_core tests
poetry run black examverse_core tests
```

---

## Repository Map

| Path | Purpose |
|---|---|
| `examverse_core/plugins/` | Plugin base, registry, auto-discovery, exceptions |
| `examverse_core/container/` | DI container, lifetime descriptors, auto-resolver |
| `examverse_core/events/` | Async event bus, domain event base, middleware |
| `examverse_core/ai/` | LLM/embedding interfaces, provider registry |
| `examverse_core/models/` | Pydantic domain models for all ExamVerse entities |
| `examverse_core/config/` | Typed settings with pydantic-settings |
| `examverse_core/logging/` | Structlog JSON logging, context variable IDs |
| `examverse_core/security/` | JWT, bcrypt, Fernet encryption, RBAC, audit |
| `examverse_core/validation/` | Email, slug, UUID, URL, filename, phone validators |
| `examverse_core/utils/` | Pagination, retry, dates, hashing, compression, reflection |
| `examverse_core/registry/` | Generic thread-safe Registry[K, V] |
| `tests/` | Pytest test suite (>90% coverage target) |
| `docs/` | Architecture docs, ADRs, developer guides |

---

## Ecosystem Services

| Repository | Role |
|---|---|
| **examverse-core** ← *this repo* | Shared runtime foundation |
| examverse-api | REST + WebSocket API service |
| examverse-ai | AI provider implementations (OpenAI, Anthropic, …) |
| examverse-db | Database migrations and Alembic config |
| examverse-ingestion | Content ingestion pipelines |
| examverse-sdk | Python SDK for API clients |
| examverse-web | Next.js web frontend |
| examverse-mobile | React Native mobile app |
| examverse-admin | Admin dashboard |
| examverse-devops | Infrastructure, CI/CD, Helm charts |

---

## License

MIT — see [LICENSE](LICENSE).

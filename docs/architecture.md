# Architecture Overview — examverse-core

## Guiding Principles

examverse-core is built on a set of non-negotiable architectural principles:

| Principle | How it manifests |
|---|---|
| **SOLID** | Every class has one responsibility; closed for modification, open for extension |
| **Clean Architecture** | Core has zero dependencies on frameworks, databases, or HTTP |
| **Domain-Driven Design** | Models represent the ubiquitous language of the exam domain |
| **Hexagonal Architecture** | Adapters implement interfaces; core depends only on abstractions |
| **Plugin-first** | New functionality enters via plugins, not modifications |
| **Dependency Injection** | All collaborators are injected, never instantiated inside consumers |
| **Event-Driven** | Services communicate via events; no direct coupling |
| **Interface-first** | Code against abstractions (`LLMProvider`) not implementations (`openai`) |

---

## Layer Map

```
┌─────────────────────────────────────────────────────────────┐
│                    PLUGIN LAYER                             │
│  SearchPlugin  │  OpenAIPlugin  │  PaymentPlugin  │  ...   │
│  (in downstream repos, loaded at runtime via entry points) │
└─────────────────────────────┬───────────────────────────────┘
                              │ implements interfaces
┌─────────────────────────────▼───────────────────────────────┐
│                    CORE LAYER  (this repo)                  │
│                                                             │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Container│  │ EventBus  │  │  Models  │  │  Config  │  │
│  └──────────┘  └───────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │ AI Ifaces│  │ Security  │  │Validation│  │  Utils   │  │
│  └──────────┘  └───────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

Core imports **nothing** from downstream repos. Downstream repos import from core.

---

## Plugin System Architecture

```
                  pyproject.toml (entry_points)
                           │
                    PluginRegistry
                    ┌──────┴──────┐
            discover()        load_from_module()
                    │              │
              entry_points    dotted path
                    │              │
             ┌──────┴──────────────┘
             │       Plugin (ABC)
             │  ┌──────────────────────┐
             │  │ register_services()  │ → ServiceContainer
             │  │ register_events()    │ → EventBus
             │  │ register_routes()    │ → Router (optional)
             │  │ initialize()         │ async startup
             │  │ shutdown()           │ async teardown
             │  └──────────────────────┘
             │
    topological sort (respects `requires:`)
             │
    ordered initialization
```

### Auto-Discovery

Plugins declare themselves via Python entry points:

```toml
[tool.poetry.plugins."examverse.plugins"]
my-plugin = "my_package.plugin:MyPlugin"
```

`PluginRegistry.load_from_entry_points()` scans all installed packages for this group and instantiates each plugin automatically.

---

## Dependency Injection Architecture

```
ServiceContainer
├── bind_singleton(IFoo, FooImpl)   → one instance per container
├── bind_transient(IBar, BarImpl)   → new instance per resolve()
├── bind_scoped(IUoW, SqlUoW)       → one instance per scope()
└── bind_factory(IReport, fn)       → callable produces instance

DependencyResolver
└── resolve(ConcreteClass)
    ├── inspect type hints of __init__
    ├── for each typed parameter → container.resolve(type)
    └── detect cycles via resolution_chain
```

### Scoped Lifetime

Scoped instances are stored in a `ContextVar` dictionary, making them async-safe without threading locks. Each `container.scope()` context manager creates a fresh store.

---

## Event Bus Architecture

```
Publisher                     EventBus                    Subscribers
  │                               │                           │
  │ publish(UserCreated)          │                           │
  ├──────────────────────────────►│                           │
  │                               │  middleware pipeline      │
  │                               │  LoggingMiddleware        │
  │                               │  CorrelationMiddleware    │
  │                               │         │                 │
  │                               │  group by priority        │
  │                               │  ┌──────────────┐        │
  │                               │  │ priority=10  │ ──────►│
  │                               │  │ asyncio.gather│        │
  │                               │  └──────────────┘        │
  │                               │  ┌──────────────┐        │
  │                               │  │ priority=100 │ ──────►│
  │                               │  └──────────────┘        │
```

Events are immutable Pydantic models. Handlers run concurrently within the same priority band. Failed handlers are retried with exponential back-off.

---

## AI Abstraction Architecture

```
examverse-core defines:          examverse-ai implements:
  LLMProvider (ABC)                OpenAIProvider
  EmbeddingProvider (ABC)          AnthropicProvider
  VectorStore (ABC)                GeminiProvider
  ConversationMemory (ABC)         PineconeVectorStore
  PromptFormatter (ABC)            ...
  TokenCounter (ABC)

ProviderRegistry
├── register_llm("openai", OpenAIProvider())
├── register_llm("anthropic", AnthropicProvider())
└── get_llm("openai")  →  OpenAIProvider
```

No AI vendor SDK is imported in core. The registry decouples the call site from the provider.

---

## Configuration Architecture

```
.env file / environment variables
          │
    pydantic-settings
          │
    CoreSettings
    ├── DatabaseSettings  (prefix: DB_)
    ├── CacheSettings     (prefix: CACHE_)
    ├── JWTSettings       (prefix: JWT_)
    └── PluginSettings    (prefix: PLUGIN_)
```

Settings are immutable once loaded. Runtime overrides are passed via constructor kwargs in tests.

---

## Security Architecture

```
examverse-core provides (reusable components only):
  JWTHelper          — token creation/validation
  PasswordHasher     — bcrypt hashing
  SymmetricEncryption— Fernet AES-128-CBC encryption
  PermissionChecker  — role → permission evaluation
  AuditEntry/Writer  — audit log model and writer interface

examverse-core does NOT implement:
  - Login flows
  - Session management
  - OAuth / OIDC
  - Token blacklisting
```

---

## Dependency Graph

```
examverse-core
├── pydantic v2           (models, settings, validation)
├── pydantic-settings     (env var loading)
├── structlog             (structured logging)
├── python-jose           (JWT signing/verification)
├── passlib[bcrypt]       (password hashing)
├── cryptography          (Fernet symmetric encryption)
├── anyio                 (async compatibility)
├── email-validator       (email validation)
├── python-slugify        (slug generation)
├── orjson                (high-performance JSON)
└── zstandard             (zstd compression)
```

All dependencies are stable, widely-used, and have no transitive conflicts with FastAPI, SQLAlchemy, or any major Python web framework.

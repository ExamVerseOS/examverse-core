# Dependency Graph

## examverse-core Internal Dependencies

```
examverse_core
├── plugins
│   ├── base        → container, events (TYPE_CHECKING only)
│   ├── registry    → plugins.base, plugins.exceptions, container, events
│   └── exceptions  (no internal deps)
│
├── container
│   ├── container   → container.descriptors, container.resolver, container.exceptions
│   ├── descriptors (no internal deps)
│   ├── resolver    → container.exceptions
│   └── exceptions  (no internal deps)
│
├── events
│   ├── bus         → events.base, events.middleware
│   ├── base        (no internal deps)
│   └── middleware  → events.base, logging.context
│
├── ai
│   ├── interfaces  (no internal deps)
│   └── registry    → ai.interfaces
│
├── models
│   ├── base        (no internal deps)
│   ├── user        → models.base
│   ├── exam        → models.base
│   ├── study       → models.base
│   ├── ai          → models.base
│   └── analytics   → models.base
│
├── config
│   └── settings    (no internal deps)
│
├── logging
│   ├── logger      → logging.context
│   └── context     (no internal deps)
│
├── security
│   ├── jwt         → security.exceptions
│   ├── permissions → models.user
│   ├── audit       (no internal deps)
│   ├── crypto      → security.exceptions
│   └── exceptions  (no internal deps)
│
├── validation
│   └── validators  (no internal deps)
│
├── utils
│   ├── pagination      (no internal deps)
│   ├── retry           (no internal deps)
│   ├── dates           (no internal deps)
│   ├── hashing         (no internal deps)
│   ├── compression     (no internal deps)
│   ├── reflection      (no internal deps)
│   ├── identifiers     (no internal deps)
│   └── serialization   (no internal deps)
│
└── registry
    └── base            (no internal deps)
```

## External Package Dependencies

| Package | Used by | Purpose |
|---|---|---|
| `pydantic` | models, config, ai, events, security, validation | Data validation and serialization |
| `pydantic-settings` | config | Env var / .env loading |
| `structlog` | logging | Structured JSON logging |
| `python-jose` | security.jwt | JWT signing and verification |
| `passlib[bcrypt]` | security.crypto | Password hashing |
| `cryptography` | security.crypto | Fernet symmetric encryption |
| `anyio` | (runtime compatibility) | Async backend abstraction |
| `email-validator` | validation | RFC-compliant email validation |
| `python-slugify` | (available) | Slug generation utilities |
| `orjson` | utils.serialization | High-performance JSON |
| `zstandard` | utils.compression | zstd compression |
| `importlib-metadata` | plugins.registry | Entry point discovery |

## Downstream Ecosystem Dependencies on Core

```
examverse-api        → examverse-core (models, config, container, events, security)
examverse-ai         → examverse-core (ai.interfaces, events, container)
examverse-db         → examverse-core (models, config)
examverse-ingestion  → examverse-core (models, events, container, utils)
examverse-sdk        → examverse-core (models, ai.interfaces)
examverse-admin      → examverse-core (models, security, config)
```

None of the downstream repositories are imported by examverse-core — the dependency arrow points only downward.

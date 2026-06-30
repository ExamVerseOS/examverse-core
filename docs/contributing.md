# Contributing to examverse-core

Thank you for contributing to the foundation of ExamVerseOS. This guide explains how to submit changes that meet our quality bar.

---

## Principles

1. **Architecture over speed** — never sacrifice design for a shortcut.
2. **Open/Closed** — extend via plugins and new classes, not modifications.
3. **Test everything** — aim for >90% coverage; 100% on critical paths.
4. **Document everything** — Google docstrings on all public symbols.

---

## Workflow

1. Fork the repository and create a feature branch from `main`.
2. Implement your change following the [Developer Guide](developer-guide.md).
3. Add or update tests — coverage must not drop below 90%.
4. Add or update docstrings — all public symbols must be documented.
5. Run the full check suite:
   ```bash
   poetry run pytest
   poetry run mypy examverse_core
   poetry run ruff check examverse_core tests
   poetry run black --check examverse_core tests
   ```
6. Submit a Pull Request with a clear description of the change and its motivation.

---

## What Belongs in Core

**Do include:**
- Shared interfaces and base classes used by ≥2 downstream services
- Generic utilities with no domain-specific assumptions
- Extension points (plugin hooks, provider interfaces, event types)
- Reusable validators, security helpers, and configuration models

**Do not include:**
- Concrete AI provider implementations (OpenAI, Anthropic, etc.)
- Database migrations or ORM table definitions
- HTTP route handlers
- Business logic specific to one service

---

## Commit Messages

Use Conventional Commits:

```
feat(plugins): add load_from_module() to PluginRegistry
fix(container): handle None return from factory descriptor
docs(architecture): add event bus sequence diagram
test(security): add PermissionChecker edge cases
refactor(events): extract _HandlerEntry into module-level class
```

---

## Architecture Decision Records

Any non-trivial architectural decision must be documented as an ADR in `docs/adr/`. See existing ADRs for the format.

---

## Review Checklist

Before requesting review, confirm:

- [ ] All new code has 100% type annotations
- [ ] All public symbols have Google docstrings
- [ ] Tests cover success paths, failure paths, and edge cases
- [ ] Coverage remains ≥90%
- [ ] `mypy --strict` passes with no errors
- [ ] `ruff` passes with no warnings
- [ ] An ADR is filed for any architectural decision
- [ ] `CHANGELOG.md` is updated

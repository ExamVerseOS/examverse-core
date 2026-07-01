"""``examverse scaffold`` — full scaffolding engine for the ExamVerseOS platform.

Every command accepts:
  --out-dir PATH   where to write files (default: current directory)
  --preview        print to stdout instead of writing to disk

Example
-------
    examverse scaffold event UserRegistered
    examverse scaffold aggregate Order --out-dir src/orders
    examverse scaffold plugin my-plugin --preview
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(
    help="Scaffolding engine — generate production-ready ExamVerseOS components.",
    no_args_is_help=True,
)
console = Console()

# ── Shared helpers ─────────────────────────────────────────────────────────────

def _class_name(slug: str) -> str:
    """Convert a slug to PascalCase, preserving existing PascalCase inputs.

    Examples:
        >>> _class_name("user-registered")
        'UserRegistered'
        >>> _class_name("UserRegistered")
        'UserRegistered'
        >>> _class_name("email_dispatch")
        'EmailDispatch'
    """
    if "-" not in slug and "_" not in slug:
        # If it already starts uppercase, treat as PascalCase and preserve it.
        # If it's all-lowercase (e.g. "user", "users"), capitalize normally.
        if slug and slug[0].isupper():
            return slug
        return slug.capitalize()
    return "".join(p.capitalize() for p in slug.replace("-", "_").split("_"))


def _module_name(slug: str) -> str:
    """Convert a slug or PascalCase name to snake_case.

    Examples:
        >>> _module_name("user-registered")
        'user_registered'
        >>> _module_name("UserRegistered")
        'user_registered'
        >>> _module_name("EmailDispatch")
        'email_dispatch'
    """
    # Insert underscore between consecutive caps and cap+lower transitions
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", slug)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.replace("-", "_").lower()


def _write_or_preview(
    files: dict[str, str],
    out_dir: Path,
    preview: bool,
    *,
    lang: str = "python",
) -> None:
    """Either write *files* to *out_dir* or pretty-print them to the terminal.

    Args:
        files: Mapping of relative path → file content.
        out_dir: Root directory for writing files.
        preview: When True, print to stdout; when False, write to disk.
        lang: Syntax highlighting language for preview mode.
    """
    if preview:
        for rel_path, content in files.items():
            ext = Path(rel_path).suffix.lstrip(".")
            highlight = ext if ext in ("py", "md", "toml", "sql") else lang
            console.print(f"\n[bold cyan]── {rel_path} ──[/bold cyan]")
            console.print(Syntax(content, highlight, theme="monokai", line_numbers=True))
        console.print()
        return

    created: list[Path] = []
    for rel_path, content in files.items():
        target = out_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        created.append(target)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Icon", style="green", no_wrap=True)
    table.add_column("Path", style="cyan")
    for p in created:
        table.add_row("✓", str(p))

    console.print(
        Panel(
            table,
            title=f"[bold green]Created {len(created)} file(s)[/bold green]",
            border_style="green",
            expand=False,
        )
    )


# ── scaffold event ─────────────────────────────────────────────────────────────

@app.command("event")
def scaffold_event(
    name: Annotated[str, typer.Argument(help="Event name in PascalCase, e.g. UserRegistered")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o", help="Output root directory."),
    preview: bool = typer.Option(False, "--preview", "-p", help="Print to stdout; do not write files."),
    version: int = typer.Option(1, "--version", "-v", help="Initial event schema version."),
) -> None:
    """Scaffold a complete event-driven component (event + handler + subscription + test + docs)."""
    cls = _class_name(name)
    mod = _module_name(name)
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    # 1. events/<mod>.py
    event_file = f"""\
\"\"\"Domain event: {cls}.

This module defines the immutable {cls} event which is published whenever
the corresponding domain action occurs.
\"\"\"

from __future__ import annotations

from examverse_core.events.bus import DomainEvent


class {cls}(DomainEvent):
    \"\"\"Raised when {name.replace("_", " ").lower()} occurs.

    Inherits from :class:`~examverse_core.events.bus.DomainEvent` and
    therefore includes ``event_id``, ``event_type``, ``occurred_at``,
    ``correlation_id``, ``metadata``, and ``version`` automatically.

    Add your domain-specific payload fields below.

    Example:
        >>> event = {cls}(user_id="abc-123")
        >>> bus.publish(event)

    Attributes:
        user_id: ID of the user who triggered this event.
    \"\"\"

    user_id: str
    \"\"\"ID of the actor who triggered this event.\"\"\"

    model_config = {{"frozen": True}}

    def __init_subclass__(cls, **kwargs: object) -> None:  # noqa: ANN003
        super().__init_subclass__(**kwargs)
"""

    # 2. handlers/<mod>_handler.py
    handler_file = f"""\
\"\"\"Event handler: {cls}Handler.

Receives :class:`~events.{mod}.{cls}` events from the event bus
and performs the required side-effects.
\"\"\"

from __future__ import annotations

import structlog

from events.{mod} import {cls}

logger = structlog.get_logger(__name__)


class {cls}Handler:
    \"\"\"Handles :class:`~events.{mod}.{cls}` events.

    Example:
        >>> handler = {cls}Handler()
        >>> await handler.handle(event)

    Attributes:
        _logger: Bound structlog logger.
    \"\"\"

    def __init__(self) -> None:
        \"\"\"Initialise the handler with a bound logger.\"\"\"
        self._logger = logger.bind(handler=self.__class__.__name__)

    async def handle(self, event: {cls}) -> None:
        \"\"\"Process a {cls} event.

        Args:
            event: The incoming domain event.

        Raises:
            NotImplementedError: Replace with real business logic.
        \"\"\"
        self._logger.info(
            "{mod}.received",
            event_id=event.event_id,
            correlation_id=event.correlation_id,
            version=event.version,
        )
        raise NotImplementedError(
            f"Implement handle() in {{self.__class__.__name__}}"
        )
"""

    # 3. subscriptions/<mod>.py
    subscription_file = f"""\
\"\"\"Subscription wiring for :class:`~events.{mod}.{cls}`.

Import this module during application startup (e.g. in your plugin's
``register_events`` method) to activate the handler.
\"\"\"

from __future__ import annotations

from examverse_core.events.bus import EventBus

from events.{mod} import {cls}
from handlers.{mod}_handler import {cls}Handler


def register(bus: EventBus) -> None:
    \"\"\"Subscribe :class:`{cls}Handler` to :class:`{cls}` on *bus*.

    Args:
        bus: The application-level event bus instance.

    Example:
        >>> from examverse_core.events.bus import EventBus
        >>> bus = EventBus()
        >>> register(bus)
    \"\"\"
    handler = {cls}Handler()
    bus.subscribe({cls}, handler.handle)


# ── Sample publisher code ──────────────────────────────────────────────────────
#
# from events.{mod} import {cls}
#
# async def publish_example(bus: EventBus, user_id: str) -> None:
#     event = {cls}(
#         user_id=user_id,
#         correlation_id="trace-abc-123",   # pass from request context
#         version={version},
#     )
#     await bus.publish(event)
#
# ── Sample subscriber code ─────────────────────────────────────────────────────
#
# from subscriptions.{mod} import register
# register(bus)   # call once at startup
"""

    # 4. tests/test_<mod>.py
    test_file = f"""\
\"\"\"Unit tests for :class:`~events.{mod}.{cls}` and its handler.\"\"\"

from __future__ import annotations

import pytest

from events.{mod} import {cls}
from handlers.{mod}_handler import {cls}Handler


class Test{cls}:
    \"\"\"Tests for the {cls} domain event.\"\"\"

    def test_event_id_generated(self) -> None:
        \"\"\"event_id is a non-empty UUID string.\"\"\"
        event = {cls}(user_id="user-1")
        assert event.event_id
        assert len(event.event_id) == 36

    def test_event_type_set(self) -> None:
        \"\"\"event_type is auto-derived from the class name.\"\"\"
        event = {cls}(user_id="user-1")
        assert "{cls}" in event.event_type or event.event_type == ""

    def test_payload_fields(self) -> None:
        \"\"\"Domain-specific fields are stored correctly.\"\"\"
        event = {cls}(user_id="user-42")
        assert event.user_id == "user-42"

    def test_correlation_id_optional(self) -> None:
        \"\"\"correlation_id defaults to None.\"\"\"
        event = {cls}(user_id="user-1")
        assert event.correlation_id is None

    def test_correlation_id_set(self) -> None:
        \"\"\"correlation_id can be provided.\"\"\"
        event = {cls}(user_id="user-1", correlation_id="trace-xyz")
        assert event.correlation_id == "trace-xyz"

    def test_version_default(self) -> None:
        \"\"\"version defaults to 1.\"\"\"
        event = {cls}(user_id="user-1")
        assert event.version == {version}

    def test_event_is_immutable(self) -> None:
        \"\"\"Event fields cannot be mutated after creation.\"\"\"
        event = {cls}(user_id="user-1")
        with pytest.raises(Exception):
            event.user_id = "other"  # type: ignore[misc]


class Test{cls}Handler:
    \"\"\"Tests for {cls}Handler.\"\"\"

    @pytest.mark.asyncio
    async def test_handle_raises_not_implemented(self) -> None:
        \"\"\"Default stub raises NotImplementedError (reminds dev to implement).\"\"\"
        handler = {cls}Handler()
        event = {cls}(user_id="user-1")
        with pytest.raises(NotImplementedError):
            await handler.handle(event)
"""

    # 5. docs/<mod>.md
    docs_file = f"""\
# {cls}

> **Status:** Draft  |  **Version:** {version}  |  **Date:** {today}

## Overview

The `{cls}` domain event is published whenever [describe the business trigger here].

## Event Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `event_id` | `str` (UUID) | auto | Unique event instance identifier |
| `event_type` | `str` | auto | Dotted-path event type name |
| `occurred_at` | `datetime` | auto | UTC creation timestamp |
| `correlation_id` | `str \\| None` | no | Distributed trace token |
| `metadata` | `dict` | no | Arbitrary headers |
| `version` | `int` | no (default: {version}) | Schema version — bump on breaking change |
| `user_id` | `str` | **yes** | ID of the actor who triggered this event |

## Publisher

```python
from events.{mod} import {cls}

event = {cls}(
    user_id=user.id,
    correlation_id=ctx.trace_id,  # from request context
)
await bus.publish(event)
```

## Subscriber

```python
from subscriptions.{mod} import register
register(bus)  # call once at startup or in plugin.register_events()
```

## Handler

Implement your business logic in `handlers/{mod}_handler.py`:

```python
async def handle(self, event: {cls}) -> None:
    # 1. Validate preconditions
    # 2. Apply side effects (DB writes, emails, etc.)
    # 3. Publish downstream events if needed
    ...
```

## Versioning

Bump `version` in the event payload **and** in `subscriptions/{mod}.py` when
the event shape changes in a breaking way. Consumers must handle both versions
during the migration window.

## ADR Reference

> Create an ADR in `docs/adr/` if this event crosses bounded-context boundaries
> or has non-obvious ordering constraints.

## Tests

Run: `pytest tests/test_{mod}.py -v`
"""

    files = {
        f"events/{mod}.py": event_file,
        f"handlers/{mod}_handler.py": handler_file,
        f"subscriptions/{mod}.py": subscription_file,
        f"tests/test_{mod}.py": test_file,
        f"docs/{mod}.md": docs_file,
    }

    _write_or_preview(files, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold aggregate ─────────────────────────────────────────────────────────

@app.command("aggregate")
def scaffold_aggregate(
    name: Annotated[str, typer.Argument(help="Aggregate name, e.g. Order")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a DDD aggregate root with domain event emission."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Aggregate root: {cls}.\"\"\"

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field

from examverse_core.models.base import AggregateRoot
from examverse_core.events.bus import DomainEvent


class {cls}Created(DomainEvent):
    \"\"\"{cls} was created.\"\"\"\n    {mod}_id: UUID\n    model_config = {{"frozen": True}}


class {cls}(AggregateRoot):
    \"\"\"Aggregate root for the {name} bounded context.

    Attributes:
        id: Primary key (UUID v4).
        name: Human-readable label.
    \"\"\"

    id: UUID = Field(default_factory=uuid4)
    name: str

    # Pending domain events — publish after the transaction commits.
    _pending_events: list[DomainEvent] = []  # not a Pydantic field

    @classmethod
    def create(cls, name: str) -> {cls}:
        \"\"\"Factory method — the only way to produce a valid {cls}.

        Args:
            name: Human-readable label for the aggregate.

        Returns:
            A new {cls} instance with a pending {cls}Created event.
        \"\"\"
        agg = cls(name=name)
        agg._pending_events.append({cls}Created({mod}_id=agg.id))
        return agg

    def pull_events(self) -> list[DomainEvent]:
        \"\"\"Return and clear all pending domain events.

        Returns:
            List of events to be published after the unit of work commits.
        \"\"\"
        events, self._pending_events = self._pending_events, []
        return events
"""

    _write_or_preview({f"{mod}/aggregate.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold model ─────────────────────────────────────────────────────────────

@app.command("model")
def scaffold_model(
    name: Annotated[str, typer.Argument(help="Model name, e.g. UserProfile")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold an immutable Pydantic v2 domain model."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Domain model: {cls}.\"\"\"

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class {cls}(BaseModel):
    \"\"\"Immutable domain model representing a {name} value object.

    Attributes:
        id: Unique identifier.
        created_at: UTC creation timestamp.
    \"\"\"

    model_config = {{"frozen": True}}

    id: UUID = Field(default_factory=uuid4, description="Primary key")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC creation timestamp",
    )

    # TODO: add domain fields here
"""

    _write_or_preview({f"models/{mod}.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold command (CQRS) ────────────────────────────────────────────────────

@app.command("command")
def scaffold_command(
    name: Annotated[str, typer.Argument(help="Command name, e.g. RegisterUser")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a CQRS command + command handler."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"CQRS command: {cls}.\"\"\"

from __future__ import annotations

from pydantic import BaseModel


class {cls}(BaseModel):
    \"\"\"Command that triggers the {name} use case.

    Attributes:
        correlation_id: Optional tracing token propagated from the request.
    \"\"\"

    model_config = {{"frozen": True}}

    correlation_id: str | None = None
    # TODO: add command payload fields here


class {cls}Handler:
    \"\"\"Handles the :class:`{cls}` command.

    Example:
        >>> handler = {cls}Handler(service)
        >>> result = await handler.handle({cls}())
    \"\"\"

    async def handle(self, command: {cls}) -> None:
        \"\"\"Execute the {name} use case.

        Args:
            command: The validated command payload.

        Raises:
            NotImplementedError: Replace with real logic.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"commands/{mod}.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold query (CQRS) ─────────────────────────────────────────────────────

@app.command("query")
def scaffold_query(
    name: Annotated[str, typer.Argument(help="Query name, e.g. GetUserById")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a CQRS query + query handler."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"CQRS query: {cls}.\"\"\"

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class {cls}(BaseModel):
    \"\"\"Read-side query for the {name} use case.\"\"\"

    model_config = {{"frozen": True}}

    # TODO: add query filter fields here


class {cls}Result(BaseModel):
    \"\"\"Read-model returned by :class:`{cls}Handler`.\"\"\"

    # TODO: add result fields here


class {cls}Handler:
    \"\"\"Executes the :class:`{cls}` read-side query.

    Example:
        >>> handler = {cls}Handler(repo)
        >>> result = await handler.handle({cls}())
    \"\"\"

    async def handle(self, query: {cls}) -> {cls}Result:
        \"\"\"Execute the query and return the read model.

        Args:
            query: Validated query parameters.

        Returns:
            A :class:`{cls}Result` view model.

        Raises:
            NotImplementedError: Replace with real data access logic.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"queries/{mod}.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold provider ─────────────────────────────────────────────────────────

@app.command("provider")
def scaffold_provider(
    name: Annotated[str, typer.Argument(help="Provider name, e.g. OpenAILLM")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold an AI/external service provider implementing the core interface."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Provider: {cls}.

Implements :class:`~examverse_core.ai.interfaces.LLMProvider` (or swap for
``EmbeddingProvider`` / ``VectorStore`` as appropriate).
\"\"\"

from __future__ import annotations

from examverse_core.ai.interfaces import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelInfo,
)


class {cls}(LLMProvider):
    \"\"\"Concrete LLM provider backed by {name}.

    Args:
        api_key: Authentication token for the upstream service.
        model: Model identifier string.
    \"\"\"

    def __init__(self, api_key: str, model: str = "default") -> None:
        self._api_key = api_key
        self._model = model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        \"\"\"Send a completion request to the {name} API.

        Args:
            request: Prompt and generation parameters.

        Returns:
            The model's completion response.

        Raises:
            NotImplementedError: Replace with HTTP call to upstream API.
        \"\"\"
        raise NotImplementedError

    async def list_models(self) -> list[ModelInfo]:
        \"\"\"Return available models from {name}.

        Returns:
            List of model info descriptors.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"providers/{mod}.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold worker ───────────────────────────────────────────────────────────

@app.command("worker")
def scaffold_worker(
    name: Annotated[str, typer.Argument(help="Worker name, e.g. EmailDispatch")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold an async background worker."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Background worker: {cls}Worker.\"\"\"

from __future__ import annotations

import asyncio

import structlog

logger = structlog.get_logger(__name__)


class {cls}Worker:
    \"\"\"Long-running async background worker for {name} processing.

    Example:
        >>> worker = {cls}Worker()
        >>> await worker.start()

    Attributes:
        _running: Whether the worker event loop is active.
    \"\"\"

    def __init__(self) -> None:
        self._running = False
        self._log = logger.bind(worker=self.__class__.__name__)

    async def start(self) -> None:
        \"\"\"Start the worker loop. Runs until :meth:`stop` is called.\"\"\"
        self._running = True
        self._log.info("worker.started")
        while self._running:
            await self._process_one()
            await asyncio.sleep(1)  # back-off; replace with queue poll

    async def stop(self) -> None:
        \"\"\"Signal the worker to stop after the current iteration.\"\"\"
        self._running = False
        self._log.info("worker.stopped")

    async def _process_one(self) -> None:
        \"\"\"Process a single work item.

        Raises:
            NotImplementedError: Implement the processing logic here.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"workers/{mod}_worker.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold scheduler ────────────────────────────────────────────────────────

@app.command("scheduler")
def scaffold_scheduler(
    name: Annotated[str, typer.Argument(help="Scheduler name, e.g. DailyReport")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a periodic scheduled task."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Scheduled task: {cls}Task.\"\"\"

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class {cls}Task:
    \"\"\"Periodic task that runs {name} on a fixed cadence.

    Args:
        interval_seconds: How often the task fires (default: 3600 = 1 h).

    Example:
        >>> task = {cls}Task(interval_seconds=300)
        >>> await task.run_forever()
    \"\"\"

    def __init__(self, interval_seconds: int = 3600) -> None:
        self._interval = interval_seconds
        self._log = logger.bind(task=self.__class__.__name__)

    async def run_forever(self) -> None:
        \"\"\"Loop forever, calling :meth:`execute` on each tick.\"\"\"
        self._log.info("scheduler.started", interval=self._interval)
        while True:
            started = datetime.now(tz=timezone.utc)
            try:
                await self.execute()
            except Exception as exc:
                self._log.exception("scheduler.failed", error=str(exc))
            elapsed = (datetime.now(tz=timezone.utc) - started).total_seconds()
            await asyncio.sleep(max(0, self._interval - elapsed))

    async def execute(self) -> None:
        \"\"\"Business logic executed on every tick.

        Raises:
            NotImplementedError: Replace with real work.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"tasks/{mod}_task.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold validator ────────────────────────────────────────────────────────

@app.command("validator")
def scaffold_validator(
    name: Annotated[str, typer.Argument(help="Validator name, e.g. ExamCode")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a reusable domain validator function."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Domain validator: {cls}.\"\"\"

from __future__ import annotations

import re


_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{{2,31}}$")
\"\"\"Regex that all valid {name} values must match.\"\"\"


def validate_{mod}(value: str) -> str:
    \"\"\"Validate and normalise a {name} value.

    Args:
        value: The raw input string to validate.

    Returns:
        The normalised (uppercased) value if valid.

    Raises:
        ValueError: When *value* does not satisfy the {name} constraints.

    Example:
        >>> validate_{mod}("EXAM_001")
        'EXAM_001'
        >>> validate_{mod}("invalid!")
        Traceback (most recent call last):
            ...
        ValueError: Invalid {name}: 'invalid!'
    \"\"\"
    normalised = value.strip().upper()
    if not _PATTERN.match(normalised):
        raise ValueError(f"Invalid {name}: {{value!r}}")
    return normalised
"""

    _write_or_preview({f"validation/{mod}_validator.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold policy ───────────────────────────────────────────────────────────

@app.command("policy")
def scaffold_policy(
    name: Annotated[str, typer.Argument(help="Policy name, e.g. ExamAccess")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a domain policy (business rule encapsulation)."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Domain policy: {cls}Policy.\"\"\"

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class {cls}PolicyResult:
    \"\"\"Outcome of a {cls}Policy evaluation.

    Attributes:
        allowed: Whether the action is permitted.
        reason: Human-readable explanation; None when *allowed* is True.
    \"\"\"

    allowed: bool
    reason: str | None = None


class {cls}Policy:
    \"\"\"Encapsulates the {name} business rule.

    Example:
        >>> policy = {cls}Policy()
        >>> result = policy.evaluate(subject, resource)
        >>> if not result.allowed:
        ...     raise PermissionError(result.reason)
    \"\"\"

    def evaluate(self, subject: object, resource: object) -> {cls}PolicyResult:
        \"\"\"Evaluate whether *subject* may access *resource*.

        Args:
            subject: The actor requesting access (e.g. a User).
            resource: The thing being accessed (e.g. an Exam).

        Returns:
            A :class:`{cls}PolicyResult` describing the decision.

        Raises:
            NotImplementedError: Implement the rule logic here.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"policies/{mod}_policy.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold exception ────────────────────────────────────────────────────────

@app.command("exception")
def scaffold_exception(
    name: Annotated[str, typer.Argument(help="Domain context name, e.g. Exam")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a typed exception hierarchy for a domain context."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Exception hierarchy for the {name} domain context.\"\"\"

from __future__ import annotations


class {cls}Error(Exception):
    \"\"\"Base exception for all {name} domain errors.

    All exceptions raised by the {name} bounded context inherit from
    this class, making it easy to catch them at the application boundary.
    \"\"\"


class {cls}NotFoundError({cls}Error):
    \"\"\"Raised when a {name} entity cannot be located.

    Args:
        entity_id: The identifier that was looked up.
    \"\"\"

    def __init__(self, entity_id: object) -> None:
        super().__init__(f"{cls} not found: {{entity_id!r}}")
        self.entity_id = entity_id


class {cls}AlreadyExistsError({cls}Error):
    \"\"\"Raised when a {name} entity already exists with the same key.

    Args:
        entity_id: The duplicate identifier.
    \"\"\"

    def __init__(self, entity_id: object) -> None:
        super().__init__(f"{cls} already exists: {{entity_id!r}}")
        self.entity_id = entity_id


class {cls}ValidationError({cls}Error):
    \"\"\"Raised when a {name} payload violates domain invariants.

    Args:
        detail: Human-readable description of what is invalid.
    \"\"\"

    def __init__(self, detail: str) -> None:
        super().__init__(f"Invalid {cls}: {{detail}}")
        self.detail = detail


class {cls}AccessDeniedError({cls}Error):
    \"\"\"Raised when an actor is not authorised to perform a {name} action.\"\"\"
"""

    _write_or_preview({f"exceptions/{mod}_errors.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold config ───────────────────────────────────────────────────────────

@app.command("config")
def scaffold_config(
    name: Annotated[str, typer.Argument(help="Config context name, e.g. Payment")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a pydantic-settings config class for a plugin or service."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Configuration for the {name} context.\"\"\"

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class {cls}Settings(BaseSettings):
    \"\"\"Runtime settings for the {name} context.

    Values are loaded from environment variables prefixed with
    ``{mod.upper()}_``. Defaults are suitable for local development.

    Example:
        >>> settings = {cls}Settings()
        >>> print(settings.api_key)
    \"\"\"

    model_config = SettingsConfigDict(
        env_prefix="{mod.upper()}_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str = Field(
        default="",
        description="API key for the upstream service.",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        description="Request timeout in seconds.",
    )
    debug: bool = Field(
        default=False,
        description="Enable verbose debug logging.",
    )
"""

    _write_or_preview({f"config/{mod}_settings.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold test ─────────────────────────────────────────────────────────────

@app.command("test")
def scaffold_test(
    name: Annotated[str, typer.Argument(help="Module/class being tested, e.g. UserService")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a pytest test module with async support and fixtures."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Tests for :class:`~{mod}.{cls}`.\"\"\"

from __future__ import annotations

import pytest


@pytest.fixture
def subject() -> {cls}:
    \"\"\"Return a default-configured {cls} for testing.\"\"\"
    raise NotImplementedError("replace with real fixture")


class Test{cls}:
    \"\"\"Unit tests for :class:`{cls}`.\"\"\"

    def test_placeholder(self, subject: {cls}) -> None:
        \"\"\"Replace with real assertions.\"\"\"
        assert subject is not None

    @pytest.mark.asyncio
    async def test_async_placeholder(self, subject: {cls}) -> None:
        \"\"\"Replace with real async assertions.\"\"\"
        assert subject is not None
"""

    _write_or_preview({f"tests/test_{mod}.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold migration ────────────────────────────────────────────────────────

@app.command("migration")
def scaffold_migration(
    name: Annotated[str, typer.Argument(help="Migration description, e.g. add-users-table")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a database migration stub (Alembic-style)."""
    mod = _module_name(name)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"migrations/{timestamp}_{mod}.py"

    code = f"""\
\"\"\"Migration: {name}.

Revision: {timestamp}
\"\"\"

from __future__ import annotations

from typing import Sequence


revision: str = "{timestamp}"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    \"\"\"Apply the migration — add tables, columns, or indices.

    Raises:
        NotImplementedError: Replace with real DDL.
    \"\"\"
    raise NotImplementedError


def downgrade() -> None:
    \"\"\"Reverse the migration — drop tables, columns, or indices.

    Raises:
        NotImplementedError: Replace with real rollback DDL.
    \"\"\"
    raise NotImplementedError
"""

    _write_or_preview({filename: code}, out_dir, preview)
    raise typer.Exit(0)


# ── scaffold api ──────────────────────────────────────────────────────────────

@app.command("api")
def scaffold_api(
    name: Annotated[str, typer.Argument(help="Resource name, e.g. users")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a FastAPI-compatible router with CRUD endpoints."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"API router for the {name} resource.

Mount this router in your application factory:

    from routers.{mod} import router as {mod}_router
    app.include_router({mod}_router, prefix="/{name}", tags=["{name}"])
\"\"\"

from __future__ import annotations

from uuid import UUID

try:
    from fastapi import APIRouter, HTTPException, status
    from pydantic import BaseModel
except ImportError as exc:
    raise ImportError("fastapi is required: pip install fastapi") from exc


router = APIRouter()


class {cls}In(BaseModel):
    \"\"\"Request body for creating or updating a {cls}.\"\"\"\n    name: str


class {cls}Out(BaseModel):
    \"\"\"Response schema for a {cls} resource.\"\"\"\n    id: UUID\n    name: str


@router.get("/", response_model=list[{cls}Out], summary="List all {name}")
async def list_{mod}() -> list[{cls}Out]:
    \"\"\"Return all {name} resources.\"\"\"
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/", response_model={cls}Out, status_code=status.HTTP_201_CREATED, summary="Create a {cls}")
async def create_{mod}(body: {cls}In) -> {cls}Out:
    \"\"\"Create a new {cls} resource.\"\"\"
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{{id}}", response_model={cls}Out, summary="Get a {cls} by ID")
async def get_{mod}(id: UUID) -> {cls}Out:
    \"\"\"Fetch a single {cls} by its UUID.\"\"\"
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.patch("/{{id}}", response_model={cls}Out, summary="Update a {cls}")
async def update_{mod}(id: UUID, body: {cls}In) -> {cls}Out:
    \"\"\"Partially update a {cls} resource.\"\"\"
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{{id}}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a {cls}")
async def delete_{mod}(id: UUID) -> None:
    \"\"\"Permanently delete a {cls} resource.\"\"\"
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
"""

    _write_or_preview({f"routers/{mod}_router.py": code}, out_dir, preview)
    raise typer.Exit(0)


# ── Existing print-to-stdout commands (kept for backward compat) ───────────────

@app.command("plugin")
def scaffold_plugin(
    name: Annotated[str, typer.Argument(help="Plugin slug, e.g. my-plugin")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold an ExamVerse plugin package."""
    cls = _class_name(name) + "Plugin"
    mod = _module_name(name)

    code = f"""\
\"\"\"ExamVerse plugin: {name}.\"\"\"

from __future__ import annotations

from examverse_core.plugins.base import Plugin, PluginMetadata
from examverse_core.container.container import ServiceContainer
from examverse_core.events.bus import EventBus


class {cls}(Plugin):
    \"\"\"ExamVerse plugin — {name}.\"\"\"

    @property
    def metadata(self) -> PluginMetadata:
        \"\"\"Return plugin metadata.\"\"\"\n        return PluginMetadata(
            name="{name}",
            version="0.1.0",
            description="Describe what this plugin does.",
            author="Your Name <you@example.com>",
        )

    async def initialize(self) -> None:
        \"\"\"Called once when the plugin starts.\"\"\"

    async def shutdown(self) -> None:
        \"\"\"Called once when the plugin stops.\"\"\"

    def register_services(self, container: ServiceContainer) -> None:
        \"\"\"Bind services into the DI container.\"\"\"\n        # container.bind_singleton(IMyService, MyService)

    def register_events(self, bus: EventBus) -> None:
        \"\"\"Subscribe to domain events.\"\"\"\n        # bus.subscribe(MyEvent, self._handle_my_event)
"""

    toml = f"""\
# pyproject.toml — register this plugin:
# [tool.poetry.plugins."examverse.plugins"]
# {name} = "{mod}.plugin:{cls}"
#
# CLI extension (optional):
# [tool.poetry.plugins."examverse.cli"]
# {name} = "{mod}.cli:app"
"""

    files = {f"{mod}/plugin.py": code, "pyproject.toml.snippet": toml}
    _write_or_preview(files, out_dir, preview)
    raise typer.Exit(0)


@app.command("service")
def scaffold_service(
    name: Annotated[str, typer.Argument(help="Service slug, e.g. user-service")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a service interface and concrete implementation."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Service: {cls}.\"\"\"

from __future__ import annotations

from abc import ABC, abstractmethod


class I{cls}(ABC):
    \"\"\"Interface for the {name} service.\"\"\"

    @abstractmethod
    async def execute(self) -> None:
        \"\"\"Perform the primary operation.\"\"\"


class {cls}(I{cls}):
    \"\"\"Concrete implementation of :class:`I{cls}`.\"\"\"\n
    async def execute(self) -> None:
        \"\"\"Perform the primary operation.

        Raises:
            NotImplementedError: Replace with real business logic.
        \"\"\"
        raise NotImplementedError
"""

    _write_or_preview({f"services/{mod}.py": code}, out_dir, preview)
    raise typer.Exit(0)


@app.command("repository")
def scaffold_repository(
    name: Annotated[str, typer.Argument(help="Aggregate/entity name, e.g. user")],
    out_dir: Path = typer.Option(Path("."), "--out-dir", "-o"),
    preview: bool = typer.Option(False, "--preview", "-p"),
) -> None:
    """Scaffold a repository interface and in-memory implementation."""
    cls = _class_name(name)
    mod = _module_name(name)

    code = f"""\
\"\"\"Repository: {cls}.\"\"\"

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class I{cls}Repository(ABC):
    \"\"\"Persistence interface for {cls} aggregates.\"\"\"

    @abstractmethod
    async def get(self, id: UUID) -> {cls} | None:
        \"\"\"Fetch by primary key. Returns None if not found.\"\"\"

    @abstractmethod
    async def save(self, entity: {cls}) -> None:
        \"\"\"Persist a new or updated entity.\"\"\"

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        \"\"\"Remove an entity by primary key.\"\"\"

    @abstractmethod
    async def list_all(self) -> list[{cls}]:
        \"\"\"Return all entities — use with caution in production.\"\"\"


class InMemory{cls}Repository(I{cls}Repository):
    \"\"\"In-memory implementation — suitable for tests and local dev.\"\"\"

    def __init__(self) -> None:
        self._store: dict[UUID, {cls}] = {{}}

    async def get(self, id: UUID) -> {cls} | None:
        return self._store.get(id)

    async def save(self, entity: {cls}) -> None:
        self._store[entity.id] = entity

    async def delete(self, id: UUID) -> None:
        self._store.pop(id, None)

    async def list_all(self) -> list[{cls}]:
        return list(self._store.values())
"""

    _write_or_preview({f"repositories/{mod}_repository.py": code}, out_dir, preview)
    raise typer.Exit(0)

"""``examverse events`` sub-group — inspect the event bus."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Inspect the ExamVerse event bus.", no_args_is_help=True)
console = Console()


@app.command("list")
def list_events() -> None:
    """List all event types that have registered handlers on the global bus."""
    try:
        from examverse_core.events.bus import EventBus

        bus = EventBus()
        subscriptions: dict[str, int] = {}

        raw = getattr(bus, "_handlers", {})
        for event_type, handlers in raw.items():
            name = getattr(event_type, "__name__", str(event_type))
            subscriptions[name] = len(handlers)

    except Exception as exc:
        console.print(f"[red]Could not inspect event bus:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print()

    if not subscriptions:
        console.print(
            "[yellow]No event handlers registered.[/yellow]\n"
            "[dim]Handlers are registered at runtime by plugins or application code.[/dim]\n"
        )
        raise typer.Exit(0)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Event type", style="cyan", no_wrap=True)
    table.add_column("Handlers", style="white", justify="right")

    for event_name, count in sorted(subscriptions.items()):
        table.add_row(event_name, str(count))

    console.print(table)
    console.print(f"\n[dim]{len(subscriptions)} event type(s) registered.[/dim]\n")
    raise typer.Exit(0)

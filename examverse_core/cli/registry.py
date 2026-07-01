"""``examverse registry`` sub-group — inspect the generic registry."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(help="Inspect the ExamVerse generic registry.", no_args_is_help=True)
console = Console()


@app.command("dump")
def dump(
    format: str = typer.Option("table", "--format", "-f", help="Output format: table | json"),
) -> None:
    """Dump all entries registered in the global ExamVerse registry."""
    try:
        from examverse_core.registry.base import Registry

        reg: Registry[object] = Registry()
        entries = dict(reg)
    except Exception as exc:
        console.print(f"[red]Registry unavailable:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print()

    if not entries:
        console.print("[yellow]Registry is empty.[/yellow]\n")
        raise typer.Exit(0)

    if format == "json":
        payload = {k: repr(v) for k, v in entries.items()}
        console.print(Syntax(json.dumps(payload, indent=2), "json", theme="monokai"))
    else:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Type", style="white")
        table.add_column("Repr", style="dim")

        for key, val in entries.items():
            table.add_row(str(key), type(val).__name__, repr(val)[:60])

        console.print(table)

    console.print()
    raise typer.Exit(0)

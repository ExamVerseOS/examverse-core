"""``examverse config`` sub-group — inspect runtime configuration."""

from __future__ import annotations

import json
import os

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(help="Inspect ExamVerse runtime configuration.", no_args_is_help=True)
console = Console()


@app.command("show")
def show(
    format: str = typer.Option("table", "--format", "-f", help="Output format: table | json | env"),
    env: bool = typer.Option(False, "--env", help="Show current environment variable overrides."),
) -> None:
    """Display the active CoreSettings configuration."""
    try:
        from examverse_core.config.settings import CoreSettings
        settings = CoreSettings()  # type: ignore[call-arg]
    except Exception as exc:
        console.print(f"[red]Could not load CoreSettings:[/red] {exc}")
        raise typer.Exit(1) from exc

    data: dict[str, object] = {}
    for field_name in type(settings).model_fields:
        val = getattr(settings, field_name, None)
        data[field_name] = str(val) if val is not None else ""

    if format == "json":
        console.print(Syntax(json.dumps(data, indent=2), "json", theme="monokai"))
    elif format == "env":
        for k, v in data.items():
            console.print(f"{k.upper()}={v}")
    else:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Source", style="dim")

        for k, v in data.items():
            env_key = k.upper()
            source = "env" if env_key in os.environ else "default"
            table.add_row(k, str(v), source)

        console.print()
        console.print(table)
        console.print()

    raise typer.Exit(0)


@app.command("validate")
def validate_config() -> None:
    """Validate that the current configuration is well-formed."""
    error: Exception | None = None
    try:
        from examverse_core.config.settings import CoreSettings
        CoreSettings()  # type: ignore[call-arg]
    except Exception as exc:
        error = exc

    if error is None:
        console.print("[green]Configuration is valid.[/green]")
        raise typer.Exit(0)

    console.print(f"[red]Configuration error:[/red] {error}")
    raise typer.Exit(1)

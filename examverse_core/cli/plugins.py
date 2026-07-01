"""``examverse plugins`` sub-group — discover and validate installed plugins."""

from __future__ import annotations

from importlib.metadata import entry_points

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Discover and validate ExamVerse plugins.", no_args_is_help=True)
console = Console()

_PLUGIN_GROUP = "examverse.plugins"


def _get_plugin_eps() -> list[object]:
    return list(entry_points(group=_PLUGIN_GROUP))


@app.command("list")
def list_plugins() -> None:
    """List all plugins registered under the examverse.plugins entry point group."""
    eps = _get_plugin_eps()
    console.print()

    if not eps:
        console.print(
            f"[yellow]No plugins found.[/yellow]\n"
            f"Install packages that register an entry point under "
            f"[cyan]examverse.plugins[/cyan] to see them here.\n"
        )
        raise typer.Exit(0)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Entry point", style="white")
    table.add_column("Package", style="dim")

    for ep in eps:
        dist = getattr(ep, "dist", None)
        pkg = getattr(dist, "name", "unknown") if dist else "unknown"
        table.add_row(ep.name, getattr(ep, "value", ""), pkg)

    console.print(table)
    console.print(f"\n[dim]{len(eps)} plugin(s) found.[/dim]\n")
    raise typer.Exit(0)


@app.command("validate")
def validate_plugins() -> None:
    """Load every registered plugin and verify its metadata is well-formed."""
    eps = _get_plugin_eps()
    console.print()

    if not eps:
        console.print("[yellow]No plugins to validate.[/yellow]\n")
        raise typer.Exit(0)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Class", style="white")
    table.add_column("Version", style="dim")
    table.add_column("Status", no_wrap=True)

    failures = 0
    for ep in eps:
        try:
            cls = ep.load()
            instance = cls()
            meta = instance.metadata
            table.add_row(
                ep.name,
                cls.__qualname__,
                meta.version,
                "[green]OK[/green]",
            )
        except Exception as exc:
            table.add_row(ep.name, "", "", f"[red]FAIL  {str(exc)[:40]}[/red]")
            failures += 1

    console.print(table)
    console.print()
    if failures:
        console.print(f"[red]{failures} plugin(s) failed validation.[/red]\n")
        raise typer.Exit(1)
    console.print(f"[green]All {len(eps)} plugin(s) are valid.[/green]\n")
    raise typer.Exit(0)

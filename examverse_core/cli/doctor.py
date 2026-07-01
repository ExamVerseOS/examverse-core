"""``examverse doctor`` — diagnose the installation health."""

from __future__ import annotations

import importlib
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()

_CHECKS: list[tuple[str, str]] = [
    ("examverse_core", "Core package"),
    ("examverse_core.plugins.base", "Plugin base"),
    ("examverse_core.plugins.registry", "Plugin registry"),
    ("examverse_core.container.container", "DI container"),
    ("examverse_core.container.resolver", "Dependency resolver"),
    ("examverse_core.events.bus", "Event bus"),
    ("examverse_core.ai.interfaces", "AI interfaces"),
    ("examverse_core.models.user", "User model"),
    ("examverse_core.models.exam", "Exam model"),
    ("examverse_core.models.analytics", "Analytics model"),
    ("examverse_core.config.settings", "CoreSettings"),
    ("examverse_core.logging.logger", "Structured logger"),
    ("examverse_core.security.jwt", "JWT helper"),
    ("examverse_core.security.crypto", "Crypto utilities"),
    ("examverse_core.validation.validators", "Validators"),
    ("examverse_core.utils.pagination", "Pagination"),
    ("examverse_core.utils.identifiers", "Identifiers"),
    ("examverse_core.utils.retry", "Retry"),
    ("pydantic", "pydantic (v2)"),
    ("pydantic_settings", "pydantic-settings"),
    ("structlog", "structlog"),
    ("jose", "python-jose"),
    ("passlib", "passlib[bcrypt]"),
    ("cryptography", "cryptography"),
    ("orjson", "orjson"),
    ("zstandard", "zstandard"),
]


def doctor(
    fix: bool = typer.Option(False, "--fix", help="Attempt to install missing packages."),
) -> None:
    """Run diagnostics and report the health of your ExamVerse installation."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Status", no_wrap=True)

    failures: list[tuple[str, str]] = []

    for module, description in _CHECKS:
        try:
            mod = importlib.import_module(module)
            ver = getattr(mod, "__version__", None)
            ver_str = f" {ver}" if ver else ""
            table.add_row(module, description, f"[green]OK[/green]{ver_str}")
        except Exception as exc:
            short = str(exc)[:55]
            table.add_row(module, description, f"[red]FAIL  {short}[/red]")
            failures.append((module, str(exc)))

    console.print()
    console.print(table)
    console.print()

    if not failures:
        console.print(
            f"[bold green]All {len(_CHECKS)} checks passed.[/bold green] "
            f"examverse-core is healthy on Python {sys.version.split()[0]}."
        )
        console.print()
        raise typer.Exit(0)

    console.print(
        f"[bold red]{len(failures)} of {len(_CHECKS)} checks failed.[/bold red]"
    )
    for mod, err in failures:
        console.print(f"  [red]x[/red] {mod}: {err}")
    console.print()

    if fix:
        import subprocess
        pkgs = [m.split(".")[0].replace("_", "-") for m, _ in failures]
        console.print(f"[yellow]Running:[/yellow] pip install {' '.join(pkgs)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + pkgs, check=False)
    else:
        console.print("[dim]Tip: run [bold]examverse doctor --fix[/bold] to attempt auto-repair.[/dim]")

    console.print()
    raise typer.Exit(1)

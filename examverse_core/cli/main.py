"""Main CLI entry point for examverse-core.

The CLI is intentionally small — only framework-level commands live here.
Other repositories extend it by registering a Typer sub-app under the
``examverse.cli`` entry-point group in their own ``pyproject.toml``:

    [tool.poetry.plugins."examverse.cli"]
    db = "examverse_db.cli:app"

Run ``examverse --help`` to see all available commands.
"""

from __future__ import annotations

import sys
from importlib.metadata import entry_points

import typer
from rich.console import Console

from examverse_core.cli import config, events, plugins, registry, scaffold
from examverse_core.cli.version import version_string

_CLI_EXTENSION_GROUP = "examverse.cli"

console = Console()

app = typer.Typer(
    name="examverse",
    help=(
        "ExamVerse Core — platform maintenance and developer tooling.\n\n"
        "Built-in commands cover diagnostics, configuration, plugins, scaffolding,\n"
        "and registry inspection. Other repositories extend this CLI automatically\n"
        "via the [cyan]examverse.cli[/cyan] entry-point group."
    ),
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)

# ── Built-in sub-groups ────────────────────────────────────────────────────────
app.add_typer(config.app,    name="config")
app.add_typer(plugins.app,   name="plugins")
app.add_typer(registry.app,  name="registry")
app.add_typer(events.app,    name="events")
app.add_typer(scaffold.app,  name="scaffold")


# ── Plugin-contributed sub-groups ──────────────────────────────────────────────
def _load_cli_extensions() -> None:
    """Load Typer sub-apps contributed by installed packages."""
    for ep in entry_points(group=_CLI_EXTENSION_GROUP):
        try:
            ext_app: typer.Typer = ep.load()
            app.add_typer(ext_app, name=ep.name)
        except Exception as exc:  # noqa: BLE001
            console.print(
                f"[yellow]Warning:[/yellow] CLI extension "
                f"[bold]{ep.name}[/bold] failed to load: {exc}",
                err=True,
            )


_load_cli_extensions()


# ── Top-level commands ─────────────────────────────────────────────────────────
@app.command()
def doctor(
    fix: bool = typer.Option(False, "--fix", help="Attempt to install missing packages."),
) -> None:
    """Run diagnostics and report the health of your ExamVerse installation."""
    from examverse_core.cli.doctor import doctor as _doctor
    _doctor(fix=fix)


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V", is_eager=True, help="Show version and exit."
    ),
) -> None:
    if version:
        console.print(version_string())
        raise typer.Exit(0)


def main() -> None:
    """Entry point registered in pyproject.toml under [tool.poetry.scripts]."""
    app()


if __name__ == "__main__":
    main()

"""Tests for ``examverse events``."""

from __future__ import annotations

from typer.testing import CliRunner

from examverse_core.cli.main import app

runner = CliRunner()


class TestEventsList:
    def test_exits_zero(self) -> None:
        result = runner.invoke(app, ["events", "list"])
        assert result.exit_code == 0

    def test_shows_no_handlers_on_fresh_bus(self) -> None:
        result = runner.invoke(app, ["events", "list"])
        assert "No event handlers" in result.output or "registered" in result.output

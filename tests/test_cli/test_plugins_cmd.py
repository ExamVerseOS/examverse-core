"""Tests for ``examverse plugins``."""

from __future__ import annotations

from typer.testing import CliRunner

from examverse_core.cli.main import app

runner = CliRunner()


class TestPluginsList:
    def test_exits_zero_no_plugins(self) -> None:
        result = runner.invoke(app, ["plugins", "list"])
        assert result.exit_code == 0

    def test_shows_no_plugins_message(self) -> None:
        result = runner.invoke(app, ["plugins", "list"])
        assert "No plugins" in result.output or "found" in result.output


class TestPluginsValidate:
    def test_exits_zero_no_plugins(self) -> None:
        result = runner.invoke(app, ["plugins", "validate"])
        assert result.exit_code == 0

    def test_shows_no_plugins_message(self) -> None:
        result = runner.invoke(app, ["plugins", "validate"])
        assert "No plugins" in result.output or "valid" in result.output.lower()

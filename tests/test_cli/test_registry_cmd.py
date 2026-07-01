"""Tests for ``examverse registry``."""

from __future__ import annotations

from typer.testing import CliRunner

from examverse_core.cli.main import app

runner = CliRunner()


class TestRegistryDump:
    def test_exits_zero(self) -> None:
        result = runner.invoke(app, ["registry", "dump"])
        assert result.exit_code == 0

    def test_json_format(self) -> None:
        result = runner.invoke(app, ["registry", "dump", "--format", "json"])
        assert result.exit_code == 0

    def test_shows_empty_or_entries(self) -> None:
        result = runner.invoke(app, ["registry", "dump"])
        assert "empty" in result.output.lower() or result.exit_code == 0

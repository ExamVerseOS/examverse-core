"""Tests for ``examverse config``."""

from __future__ import annotations

from typer.testing import CliRunner

from examverse_core.cli.main import app

runner = CliRunner()


class TestConfigShow:
    def test_exits_zero(self) -> None:
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

    def test_json_format(self) -> None:
        result = runner.invoke(app, ["config", "show", "--format", "json"])
        assert result.exit_code == 0
        assert "{" in result.output

    def test_env_format(self) -> None:
        result = runner.invoke(app, ["config", "show", "--format", "env"])
        assert result.exit_code == 0
        assert "=" in result.output

    def test_table_format_default(self) -> None:
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0


class TestConfigValidate:
    def test_exits_zero_with_valid_config(self) -> None:
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 0

    def test_shows_valid_message(self) -> None:
        result = runner.invoke(app, ["config", "validate"])
        assert "valid" in result.output.lower()

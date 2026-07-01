"""Tests for ``examverse doctor``."""

from __future__ import annotations

from typer.testing import CliRunner

from examverse_core.cli.main import app

runner = CliRunner()


class TestDoctor:
    def test_exits_zero_when_healthy(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    def test_shows_ok_checks(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert "OK" in result.output

    def test_shows_all_checks_passed(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert "passed" in result.output.lower()

    def test_shows_examverse_core_row(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert "examverse_core" in result.output

    def test_fix_flag_accepted(self) -> None:
        result = runner.invoke(app, ["doctor", "--fix"])
        assert result.exit_code == 0

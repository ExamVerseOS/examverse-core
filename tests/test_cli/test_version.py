"""Tests for ``examverse --version``."""

from __future__ import annotations

from typer.testing import CliRunner

from examverse_core.cli.main import app
import examverse_core

runner = CliRunner()


class TestVersion:
    def test_version_flag_exits_zero(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0

    def test_version_contains_package_version(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert examverse_core.__version__ in result.output

    def test_version_contains_python(self) -> None:
        import sys
        result = runner.invoke(app, ["--version"])
        assert sys.version.split()[0] in result.output

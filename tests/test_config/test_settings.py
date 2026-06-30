"""Tests for CoreSettings and sub-settings."""

from __future__ import annotations

import pytest

from examverse_core.config.settings import CoreSettings, Environment


class TestCoreSettings:
    def test_defaults(self) -> None:
        settings = CoreSettings()
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.log_level == "INFO"

    def test_is_development(self) -> None:
        settings = CoreSettings(environment=Environment.DEVELOPMENT)
        assert settings.is_development
        assert not settings.is_production

    def test_is_production(self) -> None:
        settings = CoreSettings(environment=Environment.PRODUCTION)
        assert settings.is_production
        assert not settings.is_development

    def test_is_testing(self) -> None:
        settings = CoreSettings(environment=Environment.TESTING)
        assert settings.is_testing

    def test_normalise_environment_from_string(self) -> None:
        settings = CoreSettings(environment="testing")  # type: ignore[arg-type]
        assert settings.environment == Environment.TESTING

    def test_invalid_log_level_raises(self) -> None:
        with pytest.raises(Exception):
            CoreSettings(log_level="VERBOSE")

    def test_nested_database_settings(self) -> None:
        settings = CoreSettings()
        assert settings.database is not None
        assert settings.database.pool_size >= 1

    def test_nested_jwt_settings(self) -> None:
        settings = CoreSettings()
        assert settings.jwt.algorithm == "HS256"

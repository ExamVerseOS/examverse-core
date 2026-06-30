"""Typed configuration system for ExamVerseOS services.

Uses Pydantic Settings for environment-variable loading, nested config
models, and runtime overrides. Every downstream service embeds or extends
:class:`CoreSettings`.

Example:
    >>> settings = CoreSettings()
    >>> print(settings.environment)
    'development'
    >>> print(settings.log_level)
    'INFO'
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, enum.Enum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseSettings(BaseSettings):
    """Relational database connection settings.

    Attributes:
        url: Full SQLAlchemy connection URL.
        pool_size: Number of persistent connections in the pool.
        max_overflow: Connections allowed beyond ``pool_size``.
        pool_timeout_seconds: Seconds to wait for a connection.
        echo_sql: Log SQL statements (development only).
    """

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    url: str = Field(
        default="sqlite+aiosqlite:///./examverse_dev.db",
        description="SQLAlchemy async connection URL",
    )
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0)
    pool_timeout_seconds: int = Field(default=30, ge=1)
    echo_sql: bool = False


class CacheSettings(BaseSettings):
    """Cache backend settings.

    Attributes:
        backend: Cache backend type (``"memory"`` or ``"redis"``).
        redis_url: Redis connection URL (used when backend is ``"redis"``).
        default_ttl_seconds: Default time-to-live for cached entries.
    """

    model_config = SettingsConfigDict(env_prefix="CACHE_", env_file=".env", extra="ignore")

    backend: str = Field(default="memory", pattern=r"^(memory|redis)$")
    redis_url: str = Field(default="redis://localhost:6379/0")
    default_ttl_seconds: int = Field(default=300, ge=1)


class JWTSettings(BaseSettings):
    """JWT authentication settings.

    Attributes:
        secret_key: HMAC secret for signing tokens.
        algorithm: JWT algorithm (default HS256).
        access_token_expire_minutes: Access token lifetime.
        refresh_token_expire_days: Refresh token lifetime.
    """

    model_config = SettingsConfigDict(env_prefix="JWT_", env_file=".env", extra="ignore")

    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_SECRET",
        min_length=32,
        description="HMAC signing secret — must be changed in production",
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)


class PluginSettings(BaseSettings):
    """Plugin discovery and loading configuration.

    Attributes:
        entry_point_group: Python entry point group to scan.
        disabled: List of plugin names to skip during discovery.
        configs: Per-plugin configuration dicts.
    """

    model_config = SettingsConfigDict(env_prefix="PLUGIN_", env_file=".env", extra="ignore")

    entry_point_group: str = Field(default="examverse.plugins")
    disabled: list[str] = Field(default_factory=list)
    configs: dict[str, dict[str, Any]] = Field(default_factory=dict)


class CoreSettings(BaseSettings):
    """Root configuration aggregating all subsystem settings.

    Populate via environment variables, a ``.env`` file, or direct
    constructor kwargs. Subsystem settings are nested and loaded from
    their own prefixed env vars automatically.

    Example:
        >>> settings = CoreSettings(environment=Environment.TESTING)
        >>> assert settings.is_testing
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Active deployment environment",
    )
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Root log level",
    )
    service_name: str = Field(
        default="examverse-core",
        max_length=100,
        description="Service identifier used in log output and tracing",
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    version: str = Field(default="0.1.0", description="Application version")
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="CORS allowed origins",
    )

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)

    @field_validator("environment", mode="before")
    @classmethod
    def normalise_environment(cls, v: str | Environment) -> Environment:
        """Coerce a string value into an :class:`Environment` enum.

        Args:
            v: The raw value from environment or constructor.

        Returns:
            A validated :class:`Environment` member.
        """
        if isinstance(v, str):
            return Environment(v.lower())
        return v

    @property
    def is_development(self) -> bool:
        """True when running in the development environment.

        Returns:
            Boolean environment check.
        """
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """True when running in the testing environment.

        Returns:
            Boolean environment check.
        """
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """True when running in the production environment.

        Returns:
            Boolean environment check.
        """
        return self.environment == Environment.PRODUCTION

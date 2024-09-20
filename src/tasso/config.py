"""Configuration definition."""

from __future__ import annotations

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from safir.logging import LogLevel, Profile

__all__ = ["Config", "config"]


class Config(BaseSettings):
    """Configuration for tasso."""

    name: str = Field("tasso", title="Name of application")

    path_prefix: str = Field("/tasso", title="URL prefix for application")

    profile: Profile = Field(
        Profile.development, title="Application logging profile"
    )

    log_level: LogLevel = Field(
        LogLevel.INFO, title="Log level of the application's logger"
    )

    logger_name: str = Field("tasso")

    # see https://safir.lsst.io/user-guide/database/initialize.html#using-non-default-postgresql-schemas
    database_schema: str | None = Field(
        default="tasso",
        description=(
            "Postgres schema name (namespace) to store classifications."
        ),
    )

    database_url: str = Field(
        default="",
        title="The URL for the tasso database",
    )

    database_user: str = Field(
        default="tasso",
        title="The username for the tasso database",
    )

    database_password: SecretStr | str | None = Field(
        default=None,
        title="The password for the tasso database",
    )

    slack_webhook_url: HttpUrl | None = Field(
        default=None,
        description=(
            "Webhook URL for sending error messages to a Slack channel."
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="TASSO_", case_sensitive=False
    )


config = Config()
"""Configuration for tasso."""

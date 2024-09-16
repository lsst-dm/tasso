"""Configuration definition."""

from __future__ import annotations

from pydantic import Field, HttpUrl
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

    slack_webhook_url: HttpUrl | None = Field(
        None,
        description=(
            "Webhook URL for sending error messages to a Slack channel."
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="TASSO_", case_sensitive=False
    )


config = Config()
"""Configuration for tasso."""

"""Tasso command-line interface."""

import click
import structlog
import uvicorn
from safir.asyncio import run_with_asyncio
from safir.click import display_help
from safir.database import (
    create_async_session,
    create_database_engine,
    initialize_database,
)

from .config import config
from .models.user import User
from .schema import Base
from .storage.user import UserStore

__all__ = ["main", "help", "init", "add_user"]


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(message="%(version)s")
def main() -> None:
    """Administrative command-line interface for tasso."""


@main.command()
@click.argument("topic", default=None, required=False, nargs=1)
@click.argument("subtopic", default=None, required=False, nargs=1)
@click.pass_context
def help(ctx: click.Context, topic: str | None, subtopic: str | None) -> None:
    """Show help for any command."""
    display_help(main, ctx, topic, subtopic)


@main.command()
@click.option(
    "--reset", is_flag=True, help="Delete all existing database data."
)
@run_with_asyncio
async def init(*, reset: bool) -> None:  # pragma: no cover
    """Initialize the database if needed."""
    logger = structlog.get_logger(config.logger_name)
    engine = create_database_engine(
        config.database_url, config.database_password
    )
    await initialize_database(
        engine, logger, schema=Base.metadata, reset=reset
    )
    await engine.dispose()


@main.command()
def run() -> None:
    """Run the application (for testing only)."""
    uvicorn.run(
        "tasso.main:app",
        reload=True,
        reload_dirs=["src"],
    )


@main.command()
@click.argument("username")
@run_with_asyncio
async def add_user(username: str) -> None:
    """Add a user."""
    u = User(username=username)
    engine = create_database_engine(
        config.database_url, config.database_password
    )
    session = await create_async_session(engine)
    store = UserStore(session)
    await store.add(u)
    await engine.dispose()


@main.command()
@run_with_asyncio
async def list_users() -> None:
    """Get users."""
    engine = create_database_engine(
        config.database_url, config.database_password
    )
    session = await create_async_session(engine)
    store = UserStore(session)
    await store.list()
    await engine.dispose()

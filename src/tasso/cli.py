"""Tasso command-line interface."""

import click
import structlog
import uvicorn
from safir.asyncio import run_with_asyncio
from safir.click import display_help
from safir.database import create_database_engine, initialize_database
from safir.dependencies.db_session import db_session_dependency

from .config import config
from .models.classification_run import ClassificationRun
from .models.subject import Subject
from .models.user import User
from .schema import Base
from .storage.classification import ClassificationStore
from .storage.classification_run import ClassificationRunStore
from .storage.subject import SubjectStore
from .storage.user import UserStore

__all__ = ["add_user", "help", "init", "main"]


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
@click.argument("name")
@run_with_asyncio
async def add_run(name: str) -> None:
    """Add a classification run."""
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    r = ClassificationRun(name=name)
    async for db_session in db_session_dependency():
        store = ClassificationRunStore(db_session)
    await store.add(r)
    await db_session_dependency.aclose()


@main.command()
@run_with_asyncio
async def list_runs() -> None:
    """Get runs."""
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        store = ClassificationRunStore(db_session)
        print(await store.list())
    await db_session_dependency.aclose()


@main.command()
@click.argument("run_id")
@click.argument("dia_source_id")
@click.argument("uri")
@run_with_asyncio
async def add_subject(run_id: str, dia_source_id: int, uri: str) -> None:
    """Add a subject."""
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    s = Subject(run_id=run_id, dia_source_id=dia_source_id, uri=uri)
    async for db_session in db_session_dependency():
        store = SubjectStore(db_session)
    await store.add(s)
    await db_session_dependency.aclose()


@main.command()
@click.argument("username")
@run_with_asyncio
async def add_user(username: str) -> None:
    """Add a user."""
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    u = User(username=username)
    async for db_session in db_session_dependency():
        store = UserStore(db_session)
    await store.add(u)
    await db_session_dependency.aclose()


@main.command()
@run_with_asyncio
async def list_users() -> None:
    """Get users."""
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        store = UserStore(db_session)
        print(await store.list())
    await db_session_dependency.aclose()


@main.command()
@run_with_asyncio
async def list_classifications() -> None:
    """Get users."""
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        store = ClassificationStore(db_session)
        print(await store.list())
    await db_session_dependency.aclose()

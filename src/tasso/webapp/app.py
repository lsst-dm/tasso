"""tasso webapp."""

import base64
import random
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from safir.dependencies.db_session import db_session_dependency
from safir.dependencies.gafaelfawr import auth_dependency
from safir.dependencies.http_client import http_client_dependency
from sqlalchemy.ext.asyncio import async_scoped_session

from tasso.config import config
from tasso.storage.classification import ClassificationStore
from tasso.storage.classification_run import ClassificationRunStore
from tasso.storage.subject import SubjectStore


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Provide FastAPI init/cleanups."""
    # Dependency inits before app starts running
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )
    assert db_session_dependency._engine is not None  # noqa: S101,SLF001
    db_session_dependency._engine.echo = config.database_echo  # type: ignore[attr-defined] # noqa: SLF001

    # App runs here...
    yield

    # Dependency cleanups after app is finished
    await db_session_dependency.aclose()
    await http_client_dependency.aclose()


webapp = FastAPI(lifespan=lifespan, title="tasso")

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

router = APIRouter(
    prefix="/tasso",
    tags=["Web Application"],
)

webapp.mount(
    "/static",
    StaticFiles(directory=str(Path(BASE_DIR, "static"))),
    name="static",
)


@webapp.get("/", response_class=HTMLResponse)
async def scan_subjects(
    request: Request,
    user: Annotated[str, Depends(auth_dependency)],
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return page for unclassified subject."""
    try:
        async for db_session in db_session_dependency():
            store = SubjectStore(db_session)
            run_store = ClassificationRunStore(db_session)

        runs = await run_store.get_active_runs()
        if len(runs) == 0:
            # throw an error for now
            raise ValueError("No currently active runs")
        if len(runs) == 1:  # noqa: SIM108
            run = runs[0]
        else:
            # choose a run at random.
            run = random.choice(runs)  # noqa: S311

        subject = await store.get_unclassified(
            user, run.run_id, run.max_classifications
        )
        if subject is None:
            # throw an error for now
            raise ValueError("No available subjects")
        image_bytes = store.get_blob(subject)
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        return templates.TemplateResponse(
            name="pages/scan.html",
            request=request,
            context={
                "subject": subject,
                "user": user,
                "image": encoded_image,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            name="pages/error.html",
            request=request,
            context={
                "traceback": e,
            },
        )


@webapp.get("/subjects/{subject_id}", response_class=HTMLResponse)
async def get_subject(
    request: Request,
    subject_id: str,
    user: Annotated[str, Depends(auth_dependency)],
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return page for single subject."""
    try:
        async for db_session in db_session_dependency():
            store = SubjectStore(db_session)
            subject = await store.get(subject_id)
            image_bytes = store.get_blob(subject)
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        return templates.TemplateResponse(
            name="pages/subject.html",
            request=request,
            context={
                "subject": subject,
                "user": user,
                "image": encoded_image,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            name="pages/error.html",
            request=request,
            context={
                "traceback": e,
            },
        )


@webapp.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    user: Annotated[str, Depends(auth_dependency)],
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return the about page."""
    try:
        return templates.TemplateResponse(
            name="pages/about.html",
            request=request,
            context={
                "user": user,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            name="pages/error.html",
            request=request,
            context={
                "traceback": e,
            },
        )


@webapp.get("/guide", response_class=HTMLResponse)
async def guide(
    request: Request,
    user: Annotated[str, Depends(auth_dependency)],
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return the guide page."""
    try:
        return templates.TemplateResponse(
            name="pages/guide.html",
            request=request,
            context={
                "user": user,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            name="pages/error.html",
            request=request,
            context={
                "traceback": e,
            },
        )


@webapp.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(
    request: Request,
    user: Annotated[str, Depends(auth_dependency)],
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return the leaderboard page."""
    async for db_session in db_session_dependency():
        store = ClassificationStore(db_session)
        run_store = ClassificationRunStore(db_session)

    runs = await run_store.get_active_runs()
    if len(runs) == 0:
        # throw an error for now
        raise ValueError("No currently active runs")

    leaders = await store.get_leaderboard(runs)

    try:
        return templates.TemplateResponse(
            name="pages/leaderboard.html",
            request=request,
            context={
                "leaders": leaders,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            name="pages/error.html",
            request=request,
            context={
                "traceback": e,
            },
        )


@webapp.get("/recent", response_class=HTMLResponse)
async def recent(
    request: Request,
    user: Annotated[str, Depends(auth_dependency)],
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return the recent classification page."""
    async for db_session in db_session_dependency():
        store = ClassificationStore(db_session)
        run_store = ClassificationRunStore(db_session)

    runs = await run_store.get_active_runs()
    if len(runs) == 0:
        # throw an error for now
        raise ValueError("No currently active runs")

    recent = await store.get_recent(runs)

    try:
        return templates.TemplateResponse(
            name="pages/recent.html",
            request=request,
            context={
                "recent": recent,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            name="pages/error.html",
            request=request,
            context={
                "traceback": e,
            },
        )

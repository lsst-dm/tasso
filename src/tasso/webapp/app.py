"""tasso webapp."""

import base64
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from safir.dependencies.db_session import db_session_dependency
from safir.dependencies.http_client import http_client_dependency
from sqlalchemy.ext.asyncio import async_scoped_session

from tasso.config import config
from tasso.storage.subject import SubjectStore
from tasso.storage.user import UserStore


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Provide FastAPI init/cleanups."""
    # Dependency inits before app starts running
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )
    assert db_session_dependency._engine is not None  # noqa: S101,SLF001
    db_session_dependency._engine.echo = config.database_echo  # noqa: SLF001

    # App runs here...
    yield

    # Dependency cleanups after app is finished
    await db_session_dependency.aclose()
    await http_client_dependency.aclose()


webapp = FastAPI(lifespan=lifespan, title="tasso")

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

router = APIRouter(
    prefix="/webapp",
    tags=["Web Application"],
)

webapp.mount(
    "/static",
    StaticFiles(directory=str(Path(BASE_DIR, "static"))),
    name="static",
)


@webapp.get("/", response_class=HTMLResponse)
async def get_index(request: Request) -> HTMLResponse:
    """Return index page."""
    return templates.TemplateResponse("pages/index.html", {"request": request})


# this is going to need to be paginated
@webapp.get("/subjects/", response_class=HTMLResponse)
async def get_subjects(
    request: Request,
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return subjects page."""
    try:
        async for db_session in db_session_dependency():
            store = SubjectStore(db_session)
            subjects = await store.list()

        return templates.TemplateResponse(
            name="pages/subjects.html",
            request=request,
            context={
                "subjects": subjects,
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


@webapp.get("/users/", response_class=HTMLResponse)
async def get_users(
    request: Request,
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return users page."""
    try:
        async for db_session in db_session_dependency():
            store = UserStore(db_session)
            users = await store.list()

        return templates.TemplateResponse(
            name="pages/users.html",
            request=request,
            context={
                "users": users,
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


@webapp.get("/users/{user_id}", response_class=HTMLResponse)
async def get_user(
    request: Request,
    user_id: str,
    session: Annotated[async_scoped_session, Depends(db_session_dependency)],
) -> HTMLResponse:
    """Return page for single user."""
    try:
        async for db_session in db_session_dependency():
            store = UserStore(db_session)
            user = await store.get(user_id)

        return templates.TemplateResponse(
            name="pages/user.html",
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

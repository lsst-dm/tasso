"""The main application factory for the tasso service.

Notes
-----
Be aware that, following the normal pattern for FastAPI services, the app is
constructed when this module is loaded and is not deferred until a function is
called.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import metadata, version

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from safir.dependencies.db_session import db_session_dependency
from safir.dependencies.http_client import http_client_dependency
from safir.fastapi import ClientRequestError, client_request_error_handler
from safir.logging import configure_logging, configure_uvicorn_logging
from safir.middleware.x_forwarded import XForwardedMiddleware
from safir.slack.webhook import SlackRouteErrorHandler
from structlog import get_logger

from .config import config
from .handlers.external import external_router
from .handlers.internal import internal_router
from .webapp import webapp

__all__ = ["app"]

# The lifespan context manager is used to set up and tear down anything that
# lives for the duration of the application. This is where you would put
# database connections, etc.


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Set up and tear down the application."""
    # Any code here will be run when the application starts up.
    logger = get_logger(__name__)
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    yield

    # Any code here will be run when the application shuts down.
    await db_session_dependency.aclose()
    await http_client_dependency.aclose()

    logger.info("tasso-api application shut down complete.")


# The Safir library helps you set up logging around structlog,
# https://www.structlog.org/en/stable/

configure_logging(
    profile=config.profile,
    log_level=config.log_level,
    name="tasso-api",
)
configure_uvicorn_logging(config.log_level)

app = FastAPI(
    title="tasso-api",
    description=metadata("tasso")["Summary"],
    version=version("tasso"),
    openapi_url=f"{config.path_prefix}/openapi.json",
    docs_url=f"{config.path_prefix}/docs",
    redoc_url=f"{config.path_prefix}/redoc",
    lifespan=lifespan,
)
"""The main FastAPI application for tasso."""

# Attach the routers.
app.include_router(internal_router)
app.include_router(external_router, prefix=f"{config.path_prefix}")

# Add middleware.
app.add_middleware(XForwardedMiddleware)

# This error handler reports uncaught exceptions to a Slack webhook.
if config.slack_webhook_url:
    logger = get_logger("tasso")
    SlackRouteErrorHandler.initialize(
        str(config.slack_webhook_url), "tasso", logger
    )

# Add exception handler for Safir's ClientRequestError.
app.exception_handler(ClientRequestError)(client_request_error_handler)


# Add handlers for pydantic validation errors.
# the print gives me something but the response gets eaten?
# figure out where the logs go and put them there...
@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    body = await request.body()
    print(f"Request body: {body}")  # type: ignore[str-bytes-safe]
    print(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),  # type: ignore[union-attr]
    )


# Start the frontend web application.
app.mount("/tasso", webapp)

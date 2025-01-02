"""Handlers for the app's external root, ``/tasso/``."""

from typing import Annotated

from fastapi import APIRouter, Depends
from safir.dependencies.db_session import db_session_dependency
from safir.dependencies.logger import logger_dependency
from safir.metadata import get_metadata
from structlog.stdlib import BoundLogger

from ..config import config
from ..models.classification import Classification
from ..models.index import Index
from ..storage.classification import ClassificationStore

__all__ = ["external_router", "get_index"]

external_router = APIRouter()
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    description=(
        "Document the top-level API here. By default it only returns metadata"
        " about the application."
    ),
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Index:
    """GET ``/tasso/`` (the app's external root).

    Customize this handler to return whatever the top-level resource of your
    application should return. For example, consider listing key API URLs.
    When doing so, also change or customize the response model in
    `tasso.models.Index`.

    By convention, the root of the external API includes a field called
    ``metadata`` that provides the same Safir-generated metadata as the
    internal root endpoint.
    """
    # There is no need to log simple requests since uvicorn will do this
    # automatically, but this is included as an example of how to use the
    # logger for more complex logging.
    logger.info("Request for application metadata")

    metadata = get_metadata(
        package_name="tasso",
        application_name=config.name,
    )
    return Index(metadata=metadata)


@external_router.put(
    "/classify", summary="Store classification for a given subject."
)
async def put_classification(classification: Classification) -> Classification:
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        store = ClassificationStore(db_session)
    await store.add(classification)
    await db_session_dependency.aclose()

    return classification

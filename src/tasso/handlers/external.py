"""Handlers for the app's external root, ``/tasso/``."""

import random
from typing import Annotated

from fastapi import APIRouter, Depends
from safir.dependencies.db_session import db_session_dependency
from safir.dependencies.logger import logger_dependency
from safir.metadata import get_metadata
from structlog.stdlib import BoundLogger

from ..config import config
from ..models.classification import Classification
from ..models.classification_run import ClassificationRun
from ..models.index import Index
from ..models.subject import Subject
from ..storage.classification import ClassificationStore
from ..storage.classification_run import ClassificationRunStore
from ..storage.subject import SubjectStore

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
async def put_classification(
    classification: Classification,
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Classification:
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        store = ClassificationStore(db_session)
        subject_store = SubjectStore(db_session)

    subject = await subject_store.get(classification.subject_id)
    print(subject.n_classifications)

    # silently delete any prior classifications of this subject by this user.
    # Presently each subject can only be in one run so subject and user search
    # is enough.
    prior_classifications = await store.search(
        {
            "subject_id": classification.subject_id,
            "user_id": classification.user_id,
        }
    )
    if len(prior_classifications):
        logger.info(
            f"Deleting {len(prior_classifications)} classifications "
            f"for subject {classification.subject_id} "
            f"by user {classification.user_id}."
        )
        for class_i in prior_classifications:
            await store.delete(class_i)

    await store.add(classification)
    logger.info(
        f"Created new classification {classification.classification_id} "
        f"for subject {classification.subject_id} "
        f"by user {classification.user_id}."
    )

    # count classifications of this subject by all users
    prior_classifications = await store.search(
        {"subject_id": classification.subject_id}
    )
    subject.n_classifications = len(prior_classifications)
    await subject_store.update(subject)

    await db_session_dependency.aclose()

    return classification


@external_router.get(
    "/unclassified_subject",
    summary="Return a subject that needs classification.",
)
async def get_unclassified_subject(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Subject | None:
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        store = SubjectStore(db_session)
        run_store = ClassificationRunStore(db_session)

    runs = await run_store.get_active_runs()
    if len(runs) == 0:
        return None
    elif len(runs) == 1:
        run = runs[0]
    else:
        # choose a run at random.
        run = random.choice(runs)  # noqa: S311

    # this needs to not be hardcoded.
    user_id = "dfad48bd59404103ba9c668e47f4c700"

    return await store.get_unclassified(
        user_id, run.run_id, run.max_classifications
    )


@external_router.get(
    "/active_runs",
    summary="Return runs that are active.",
)
async def get_active_runs(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> list[ClassificationRun] | None:
    await db_session_dependency.initialize(
        config.database_url, config.database_password
    )

    async for db_session in db_session_dependency():
        run_store = ClassificationRunStore(db_session)

    return await run_store.get_active_runs()

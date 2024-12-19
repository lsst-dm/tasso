"""Storage for users."""

from typing import Annotated

from fastapi import Depends
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy.ext.asyncio import async_scoped_session

from ..models.classification_run import ClassificationRun
from ..schema import ClassificationRun as SQLClassificationRun
from .base import BaseStore

__all__ = ["ClassificationRunStore"]


class ClassificationRunStore(BaseStore):
    """Stores and retrieves runs.

    Parameters
    ----------
    session
        The database session proxy.
    """

    def __init__(
        self,
        session: Annotated[
            async_scoped_session, Depends(db_session_dependency)
        ],
    ) -> None:
        super().__init__(
            session=session,
            model=ClassificationRun,
            storage=SQLClassificationRun,
            primary_key="run_id",
        )

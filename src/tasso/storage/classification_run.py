"""Storage for users."""

from typing import Annotated

from fastapi import Depends
from safir.datetime import current_datetime
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy import select
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

    async def get_active_runs(self) -> list[ClassificationRun]:
        """Return classification runs which are active.

        Returns
        -------
        list of ClassificationRun
        """
        time_now = current_datetime()

        stmt = select(self.storage).where(
            (
                (SQLClassificationRun.time_start <= time_now)
                | SQLClassificationRun.time_start.is_(None)
            ),
            (
                (SQLClassificationRun.time_stop > time_now)
                | SQLClassificationRun.time_stop.is_(None)
            ),
        )

        print(stmt)
        async with self._session.begin():
            result = await self._session.execute(stmt)
        return [self.model.model_validate(res[0]) for res in result.all()]

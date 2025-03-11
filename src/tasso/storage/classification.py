"""Storage for users."""

from typing import Annotated

from fastapi import Depends
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_scoped_session

from ..models.classification import Classification
from ..models.classification_run import ClassificationRun
from ..schema import Classification as SQLClassification
from .base import BaseStore

__all__ = ["ClassificationStore"]


class ClassificationStore(BaseStore):
    """Stores and retrieves users.

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
            model=Classification,
            storage=SQLClassification,
            primary_key="classification_id",
        )

    async def get_leaderboard(
        self, runs: ClassificationRun, limit: int = 50
    ) -> list:
        """Return classification runs which are active.

        Returns
        -------
        list of leaders
        """
        run_ids = [run.run_id for run in runs]

        count_fn = func.count(SQLClassification.subject_id)

        stmt = (
            select(SQLClassification.user, count_fn)
            .where(SQLClassification.run_id.in_(run_ids))
            .group_by(SQLClassification.user)
            .order_by(count_fn.desc())
            .limit(limit)
        )

        async with self._session.begin():
            result = await self._session.execute(stmt)
        return result.all()

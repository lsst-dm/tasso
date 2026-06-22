"""Storage for users."""

from typing import Annotated

from fastapi import Depends
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.classification import Classification, Leaderboard
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
        session: Annotated[AsyncSession, Depends(db_session_dependency)],
    ) -> None:
        super().__init__(
            session=session,
            model=Classification,
            storage=SQLClassification,
            primary_key="classification_id",
        )

    async def get_leaderboard(
        self, runs: list[ClassificationRun], limit: int = 50
    ) -> list[Leaderboard]:
        """Return leaderboard by classification count for current run.

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
            # not validated at present
        return result.all()  # type: ignore # noqa: PGH003

    async def get_recent(
        self, runs: list[ClassificationRun], limit: int = 50
    ) -> list[Classification]:
        """Return most recent classifications.

        Returns
        -------
        list of Classifications
        """
        run_ids = [run.run_id for run in runs]

        stmt = (
            select(self.storage)
            .where(SQLClassification.run_id.in_(run_ids))
            .order_by(SQLClassification.time_labeled.desc())
            .limit(limit)
        )

        async with self._session.begin():
            result = await self._session.execute(stmt)
        return [self.model.model_validate(res[0]) for res in result.all()]

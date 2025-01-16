"""Storage for subjects."""

from typing import Annotated

from fastapi import Depends
from lsst.resources import ResourcePath
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_scoped_session

from ..models.subject import Subject
from ..schema import Classification as SQLClassification
from ..schema import Subject as SQLSubject
from .base import BaseStore

__all__ = ["SubjectStore"]


class SubjectStore(BaseStore):
    """Stores and retrieves subjects.

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
            model=Subject,
            storage=SQLSubject,
            primary_key="subject_id",
        )

    def get_blob(self, subject: Subject) -> bytes:
        """Retrieve the subject image.

        Parameters
        ----------
        subject
           The subject to retrieve.
        """
        file_uri = ResourcePath(subject.uri)

        return file_uri.read()

    async def get_unclassified(
        self, user: str, run_id: str, max_classifications: int
    ) -> Subject | None:
        """Return a subject for classification.

        Choose one at random from the specified run which has fewer than the
        specified numbers of classifications and is not yet classified
        by the user.

        Parameters
        ----------
        user
           The user performing the classification.
        run_id
           The classification run to search for subjects.
        max_classifiations
            The number of classifications each subject should receive.
        """
        stmt = (
            select(SQLSubject)
            .where(
                SQLSubject.run_id == run_id,
                SQLSubject.n_classifications < max_classifications,
            )
            .outerjoin(SQLClassification)
            .where(
                (SQLClassification.user != user)
                | SQLClassification.user.is_(None)
            )
        )

        print(stmt)

        async with self._session.begin():
            result = await self._session.execute(stmt)
            value = result.one_or_none()
            print(value)
            if value is None:
                return None
            else:
                return self.model.model_validate(value[0])

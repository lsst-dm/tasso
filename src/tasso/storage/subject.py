"""Storage for subjects."""

from typing import Annotated

from fastapi import Depends
from lsst.resources import ResourcePath
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy.ext.asyncio import async_scoped_session

from ..models.subject import Subject
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

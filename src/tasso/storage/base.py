"""Base storage class."""

from typing import Annotated, ClassVar

from fastapi import Depends
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_scoped_session

__all__ = ["BaseStore"]


class BaseStore:
    """Base storage class.

    Parameters
    ----------
    session
        The database session proxy.
    model
        Pydantic model class
    storage
        Pydantic storage class
    primary key
        name of primary key
    """

    def __init__(
        self,
        session: Annotated[
            async_scoped_session, Depends(db_session_dependency)
        ],
        model: ClassVar,
        storage: ClassVar,
        primary_key: str,
    ) -> None:
        self._session = session
        self.model = model
        self.storage = storage
        self.primary_key = primary_key

    async def add(self, record: ClassVar) -> None:
        """Add a new model record.

        Parameters
        ----------
        record
            The model instance to add.
        """
        new = self.storage(**record.model_dump())
        async with self._session.begin():
            self._session.add(new)

    async def delete(self, record: ClassVar) -> bool:
        """Delete a record.

        Parameters
        ----------
        record
            The record to delete.

        Returns
        -------
        bool
            `True` if the record was found and deleted, `False`
            otherwise.
        """
        stmt = delete(self.storage).where(
            getattr(self.storage, self.primary_key)
            == getattr(record, self.primary_key)
        )
        async with self._session.begin():
            result = await self._session.execute(stmt)
            return result.rowcount > 0

    async def list(self) -> list[ClassVar]:  # -> list[self.model]:
        """Return a list of model records.

        Returns
        -------
        list of model
        """
        stmt = select(self.storage).order_by(
            getattr(self.storage, self.primary_key)
        )
        async with self._session.begin():
            result = await self._session.scalars(stmt)
            return [self.model.model_validate(a) for a in result.all()]

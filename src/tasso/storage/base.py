"""Base storage class."""

from typing import Annotated, ClassVar

from fastapi import Depends
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy import delete, select, update
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
        model: ClassVar,  # type: ignore[misc]
        storage: ClassVar,
        primary_key: str,
    ) -> None:
        self._session = session
        self.model = model
        self.storage = storage
        self.primary_key = primary_key

    async def add(self, record: ClassVar) -> None:  # type: ignore[misc]
        """Add a new model record.

        Parameters
        ----------
        record
            The model instance to add.
        """
        new = self.storage(**record.model_dump())
        async with self._session.begin():
            self._session.add(new)

    async def update(self, record: ClassVar) -> None:  # type: ignore[misc]
        """Update a model record identified by its primary key.

        Parameters
        ----------
        record
            The model instance to update.
        """
        stmt = (
            update(self.storage)
            .where(
                getattr(self.storage, self.primary_key)
                == getattr(record, self.primary_key)
            )
            .values(**record.model_dump())
        )

        async with self._session.begin():
            await self._session.execute(stmt)

    async def delete(self, record: ClassVar) -> bool:  # type: ignore[misc]
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

    async def list(self) -> list[ClassVar]:  # type: ignore[misc]
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

    async def get(self, value: str) -> ClassVar:  # type: ignore[misc]
        """Get a model record by primary key.

        Returns
        -------
        model
        """
        stmt = select(self.storage).where(
            getattr(self.storage, self.primary_key) == value
        )
        async with self._session.begin():
            result = await self._session.execute(stmt)
            row = result.one_or_none()
            print(row)
            if row is None:
                return None
            else:
                return self.model.model_validate(row[0])

    async def search(self, key_value: dict[str, str]) -> ClassVar:  # type: ignore[misc]
        """Get model records matching key-value pairs.

        Parameters
        ----------
        key
            The column name to search on
        value
            The value to search for

        Returns
        -------
        model
        """
        stmt = select(self.storage).where(
            *[
                getattr(self.storage, key) == value
                for (key, value) in key_value.items()
            ]
        )
        async with self._session.begin():
            result = await self._session.execute(stmt)
        return [self.model.model_validate(res[0]) for res in result.all()]

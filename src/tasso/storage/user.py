"""Storage for users."""

from typing import Annotated

from fastapi import Depends
from safir.dependencies.db_session import db_session_dependency
from sqlalchemy.ext.asyncio import async_scoped_session

from ..models.user import User
from ..schema import User as SQLUser
from .base import BaseStore

__all__ = ["UserStore"]


class UserStore(BaseStore):
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
            session=session, model=User, storage=SQLUser, primary_key="user_id"
        )

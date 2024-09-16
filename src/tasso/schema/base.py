"""The base for the table schemas."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from ..config import config

__all__ = ["Base"]


class Base(DeclarativeBase):
    """Declarative base for the tasso database schema."""

    metadata = MetaData(schema=config.database_schema)

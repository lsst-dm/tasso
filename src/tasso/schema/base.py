"""The base for the table schemas."""

from datetime import datetime

from sqlalchemy import TIMESTAMP, MetaData
from sqlalchemy.orm import DeclarativeBase

from ..config import config

__all__ = ["Base"]


class Base(DeclarativeBase):
    """Declarative base for the tasso database schema."""

    type_annotation_map = {datetime: TIMESTAMP(timezone=False)}  # noqa: RUF012

    metadata = MetaData(schema=config.database_schema)

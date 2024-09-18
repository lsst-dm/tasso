"""The base for the table schemas."""

from datetime import datetime
from typing import ClassVar

from sqlalchemy import TIMESTAMP, MetaData
from sqlalchemy.orm import DeclarativeBase

from ..config import config

__all__ = ["Base"]


class Base(DeclarativeBase):
    """Declarative base for the tasso database schema."""

    type_annotation_map = ClassVar({datetime: TIMESTAMP(timezone=False)})

    metadata = MetaData(schema=config.database_schema)

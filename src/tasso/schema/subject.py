"""The subjects database table."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["Subject"]


class Subject(Base):
    """Individual subject."""

    __tablename__ = "subject"

    dia_source_id: Mapped[int] = mapped_column(primary_key=True)
    uri: Mapped[str]
    run_id: Mapped[int] = mapped_column(
        ForeignKey("classification_run.run_id")
    )

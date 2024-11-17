"""The subjects database table."""

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["Subject"]


class Subject(Base):
    """Individual subject."""

    __tablename__ = "subject"

    subject_id: Mapped[int] = mapped_column(primary_key=True)
    dia_source_id: Mapped[int]
    uri: Mapped[str]

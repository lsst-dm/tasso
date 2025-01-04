"""The subjects database table."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["Subject"]


class Subject(Base):
    """Individual subject."""

    __tablename__ = "subject"

    subject_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("classification_run.run_id")
    )
    dia_source_id: Mapped[int]
    uri: Mapped[str]
    n_classifications: Mapped[int]

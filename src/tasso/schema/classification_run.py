"""Classification run table."""

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

__all__ = ["ClassificationRun"]


class ClassificationRun(Base):
    """A classification run."""

    __tablename__ = "classification_run"

    run_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str]
    comment: Mapped[str | None]
    repo: Mapped[str | None]
    collection: Mapped[str | None]
    namespace: Mapped[str | None]
    ticket: Mapped[str | None]
    time_start: Mapped[datetime | None]
    time_stop: Mapped[datetime | None]
    max_classifications: Mapped[int]

    subjects: Mapped[list["Subject"]] = relationship()  # noqa: F821

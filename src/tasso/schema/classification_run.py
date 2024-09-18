"""Classification run table."""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["ClassificationRun"]


class ClassificationRun(Base):
    """A classification run."""

    __tablename__ = "classification_run"

    run_id: Mapped[int] = mapped_column(primary_column=True)
    name: Mapped[str]
    comment: Mapped[str | None]
    repo: Mapped[str | None]
    collection: Mapped[str | None]
    namespace: Mapped[str | None]
    ticket: Mapped[str | None]
    time_start: Mapped[datetime | None]
    time_stop: Mapped[datetime | None]

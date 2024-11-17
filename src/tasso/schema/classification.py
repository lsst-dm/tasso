"""The classification database table."""

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

__all__ = ["Classification"]


class Classification(Base):
    """Individual classifications."""

    __tablename__ = "classification"

    classification_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.subject_id"))
    run_id: Mapped[int] = mapped_column(
        ForeignKey("classification_run.run_id")
    )
    label_id: Mapped[int]
    label_text: Mapped[str]
    comment: Mapped[str | None]
    flags: Mapped[int | None]
    time_labeled: Mapped[datetime]

    subjects: Mapped[list["Subject"]] = relationship()  # noqa: F821

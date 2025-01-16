"""The classification database table."""

from safir.pydantic import UtcDatetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

__all__ = ["Classification"]


class Classification(Base):
    """Individual classifications."""

    __tablename__ = "classification"

    classification_id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    subject_id: Mapped[str] = mapped_column(ForeignKey("subject.subject_id"))
    run_id: Mapped[str] = mapped_column(
        ForeignKey("classification_run.run_id")
    )
    user: Mapped[str]
    label_id: Mapped[int]
    label_text: Mapped[str]
    comment: Mapped[str | None]
    flags: Mapped[int | None]
    time_labeled: Mapped[UtcDatetime]

    subjects: Mapped[list["Subject"]] = relationship()  # type: ignore[name-defined] # noqa: F821

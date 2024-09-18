"""The classification database table."""

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .label import Label
from .run_label import RunLabel
from .subject import Subject

__all__ = ["Classification"]


class Classification(Base):
    """Individual classifications."""

    __tablename__ = "classification"

    classification_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    label_id: Mapped[int] = mapped_column(ForeignKey("label.label_id"))
    dia_source_id: Mapped[int] = mapped_column(
        ForeignKey("subject.dia_source_id")
    )
    run_id: Mapped[int] = mapped_column(
        ForeignKey("classification_run.run_id")
    )
    comment: Mapped[str | None]
    flags: Mapped[int | None]
    time_labeled: Mapped[datetime]

    subjects: Mapped[list["Subject"]] = relationship()
    labels: Mapped[list["Label"]] = relationship(
        secondary=RunLabel, back_populates="runs"
    )

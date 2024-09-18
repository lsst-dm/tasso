"""The label database table."""

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .classification import Classification
from .run_label import RunLabel

__all__ = ["Label"]


class Label(Base):
    """Individual labels."""

    __tablename__ = "label"

    label_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str]
    classifications: Mapped[list["Classification"]] = relationship(
        secondary=RunLabel, back_populates="labels"
    )

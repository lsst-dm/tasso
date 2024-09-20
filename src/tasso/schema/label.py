"""The label database table."""

# https://stackoverflow.com/questions/75919378/how-to-handle-circular-imports-in-sqlalchemy
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .classification import Classification
    from .run_label import RunLabel
else:
    Classification = "Classification"
    RunLabel = "RunLabel"

__all__ = ["Label"]


class Label(Base):
    """Individual labels."""

    __tablename__ = "label"

    label_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str]
    classifications: Mapped[list[Classification]] = relationship(
        secondary=RunLabel, back_populates="labels"
    )

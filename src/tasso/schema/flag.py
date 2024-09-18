"""The flag database table."""

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["Flag"]


class Flag(Base):
    """List of flags."""

    __tablename__ = "flag"

    flag_bit: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

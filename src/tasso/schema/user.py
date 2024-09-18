"""The user database table."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .classification import Classification

__all__ = ["User"]


class User(Base):
    """List of users."""

    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    admin: Mapped[bool]
    classifications: Mapped[list["Classification"]] = relationship()

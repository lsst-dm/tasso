"""The user database table."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .classification import Classification

__all__ = ["User"]


class User(Base):
    """List of users."""

    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64))
    admin: Mapped[bool]
    classifications: Mapped[list["Classification"]] = relationship()

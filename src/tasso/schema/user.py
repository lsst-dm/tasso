"""The user database table."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

__all__ = ["User"]


class User(Base):
    """List of users."""

    __tablename__ = "user"

    user_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    username: Mapped[str] = mapped_column(String(64))
    admin: Mapped[bool]
    classifications: Mapped[list["Classification"]] = relationship()  # noqa: F821

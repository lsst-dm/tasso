"""The user database table."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["User"]


class User(Base):
    """List of users."""

    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    admin: Mapped[bool]

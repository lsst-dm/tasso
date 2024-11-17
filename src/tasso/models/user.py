"""Representation of a label."""

from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["User"]


class User(BaseModel):
    """A user."""

    user_id: Annotated[
        str,
        Field(
            title="user id",
            description="unique user id",
            default_factory=lambda: uuid4().hex,
        ),
    ]

    username: str = Field(
        title="username",
        description="Username of the token administrator",
        examples=["dipole"],
    )

    admin: bool = Field(
        title="admin bit",
        description="is the user an admin?",
        default=False,
    )

    model_config = ConfigDict(from_attributes=True)

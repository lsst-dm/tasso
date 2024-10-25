"""Representation of a label."""

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Label"]


class Label(BaseModel):
    """A label."""

    label_id: int = Field(
        ...,
        title="label id",
        description="unique label id",
    )

    label: str = Field(
        ...,
        title="label",
        description="Username of the token administrator",
        examples=["dipole"],
    )

    model_config = ConfigDict(from_attributes=True)

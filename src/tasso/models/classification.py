"""Representation of a classification."""

from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from safir.pydantic import UtcDatetime

__all__ = ["Classification"]


class Classification(BaseModel):
    """A classification."""

    classification_id: Annotated[
        str,
        Field(
            title="classification_id",
            description="unique id for this classification",
            default_factory=lambda: uuid4().hex,
        ),
    ]

    user: str = Field(
        title="user",
        description="name of classifying user",
    )

    subject_id: str = Field(
        title="subject_id",
        description="id of classified subject",
    )

    run_id: str = Field(
        title="run_id",
        description="id of classification run",
    )

    label_id: int = Field(
        title="label_id",
        description="id of label",
    )

    label_text: str = Field(
        title="label_text",
        description="Description of label",
    )

    comment: str | None = Field(
        title="comment",
        description="User-provided comment for this subject",
        default=None,
    )

    flags: int = Field(
        title="flags",
        description="Bitpacked flags",
    )

    time_labeled: UtcDatetime = Field(
        title="time_labeled",
        description="Time label was created",
    )

    model_config = ConfigDict(from_attributes=True)

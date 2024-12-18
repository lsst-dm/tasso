"""Representation of a classification run."""

from datetime import datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["ClassificationRun"]


class ClassificationRun(BaseModel):
    """A classification run."""

    run_id: Annotated[
        str,
        Field(
            title="run_id",
            description="unique id for this classification run",
            default_factory=lambda: uuid4().hex,
        ),
    ]

    name: str = Field(
        title="name",
        description="Name of classification run.",
    )

    comment: str | None = Field(
        title="comment",
        description="Description of classification run",
        default=None,
    )

    repo: str | None = Field(
        title="repo",
        description="Base repository for subjects in this run.",
        default=None,
    )

    collection: str = Field(
        title="collection",
        description="Collection for subjects in this run.",
        default=None,
    )

    namespace: str = Field(
        title="namespace",
        description="APDB namespace for subjects in this run.",
        default=None,
    )

    ticket: str | None = Field(
        title="ticket",
        description="Ticket number for this classification run",
        default=None,
    )

    time_start: datetime | None = Field(
        title="time_start",
        description="Time run began.",
        default=None,
    )

    time_stop: datetime | None = Field(
        title="time_stop",
        description="Time run ended.",
        default=None,
    )

    max_classifications: int = Field(
        title="max_classifications",
        description="Number of classifications needed per subject.",
        default=1,
    )

    model_config = ConfigDict(from_attributes=True)

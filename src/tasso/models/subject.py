"""Representation of a Subject."""

from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Subject"]


class Subject(BaseModel):
    """A classification."""

    subject_id: Annotated[
        str,
        Field(
            title="subject_id",
            description="unique id for this subject.",
            default_factory=lambda: uuid4().hex,
        ),
    ]

    run_id: str = Field(
        title="run_id",
        description="id of classification run",
    )

    dia_source_id: int = Field(
        title="dia_source_id",
        description="DIASourceId",
    )

    data_id: str | None = Field(
        title="data_id",
        description="Data ID of the image producing the DIASource",
        default=None,
    )

    uri: str = Field(
        title="uri",
        description="Location of the cutout image.",
    )

    n_classifications: int = Field(
        title="n_classifications",
        description="Number of classifications",
        default=0,
    )

    model_config = ConfigDict(from_attributes=True)

"""Indirection database table matching runs with labels."""

from sqlalchemy import Column, ForeignKey, Table

from .base import Base

__all__ = ["RunLabel"]

RunLabel = Table(
    "run_label",
    Base.metadata,
    Column(
        "run_id", ForeignKey("classification_run.run_id"), primary_key=True
    ),
    Column("label_id", ForeignKey("label.label_id"), primary_key=True),
)

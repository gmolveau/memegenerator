"""ORM models."""

from sqlalchemy.orm import DeclarativeBase


class DBBaseModel(DeclarativeBase):
    """Base class for all ORM models."""


from src.models.template import Template  # noqa: E402, F401

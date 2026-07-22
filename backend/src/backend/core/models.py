from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


class IntIdMixin:
    """Mixin that adds a BigInteger auto-increment primary key column `id`."""

    id = Column(BigInteger, primary_key=True, autoincrement=True)

class TimeActionMixin:
    """Mixin that adds `created_at` and `updated_at` timestamp columns."""

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
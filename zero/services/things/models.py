"""SQLAlchemy ORM models for the Thing service."""

from sqlalchemy import Column, DateTime, Integer, String
from flask_sqlalchemy import SQLAlchemy, Model

db: SQLAlchemy = SQLAlchemy()


class DBThing(db.Model):
    """Model for things."""

    __tablename__ = 'things'
    id = Column(Integer, primary_key=True)
    """The unique identifier for a thing."""
    name = Column(String(255))
    """The name of the thing."""
    created = Column(DateTime)
    """The datetime when the thing was created."""

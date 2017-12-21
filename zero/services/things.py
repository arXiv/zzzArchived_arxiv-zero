"""Provides access to the Things data store."""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy, Model
from flask import Flask

from typing import Optional

db: SQLAlchemy = SQLAlchemy()

class Thing(db.Model):
    """Model for things."""

    __tablename__ = 'things'
    id = Column(Integer, primary_key=True)
    """The unique identifier for a thing."""
    name = Column(String(255))
    """The name of the thing."""
    created = Column(DateTime)
    """The datetime when the thing was created."""


def init_app(app: Flask) -> None:
    """Set configuration defaults and attach session to the application."""
    db.init_app(app)


def get_a_thing(id: int) -> Optional[dict]:
    """
    Get data about a thing.

    Parameters
    ----------
    id : int
        Unique identifier for the thing.

    Returns
    -------
    Optional[dict]
        Data about the thing.

    Raises
    ------
    IOError
        When there is a problem querying the database.

    """
    try:
        thing = db.session.query(Thing).get(id)
    except OperationalError as e:
        raise IOError('Could not query database: %s' % e.detail) from e
    if thing is None:
        return None
    return {
        'id': thing.id,
        'name': thing.name,
        'created': thing.created
    }

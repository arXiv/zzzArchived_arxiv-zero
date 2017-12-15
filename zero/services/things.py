"""Provides access to the Things data store."""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy, Model

from typing import Optional
from zero.domain import Thing

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


def init_app(app) -> None:
    """Set configuration defaults and attach session to the application."""
    db.init_app(app)


def get_a_thing(id: int) -> Thing:
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
        thing_data = db.session.query(DBThing).get(id)
    except OperationalError as e:
        raise IOError('Could not query database: %s' % e.detail) from e
    if thing_data is None:
        return None
    thing = Thing()
    thing.id = thing_data.id
    thing.name = thing_data.name
    thing.created = thing_data.created
    return thing

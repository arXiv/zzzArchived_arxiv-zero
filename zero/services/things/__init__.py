"""Provides access to the Things data store."""

from typing import Any, Dict, Optional, Generator
from contextlib import contextmanager

from flask import Flask
from sqlalchemy.exc import OperationalError

from arxiv.base import logging
from ...domain import Thing
from .models import db, DBThing

logger = logging.getLogger(__name__)


class NoSuchThing(Exception):
    """An operation was attempted on a non-existant thing."""


@contextmanager
def transaction() -> Generator:
    """
    Provide a context for an atomic operation on the database.

    To be used as a context manager. For example;

    .. code-block:: python

       from zero.services import things

       with things.transaction():
           store_a_thing(...)
           do_something_risky(...)


    In the example above, of ``do_something_risky()`` raises an exception, the
    database transaction within which ``store_a_thing()`` is operating will be
    rolled back.
    """
    try:
        yield
        # Only commit if there are un-flushed changes. The caller may have
        # already committed explicitly, e.g. to do its own exception handling.
        if db.session.dirty or db.session.deleted or db.session.new:
            db.session.commit()
    except Exception:
        db.session.rollback()
        raise     # Re-raise the original exception so that we don't interfere.


def init_app(app: Flask) -> None:
    """Set configuration defaults and attach session to the application."""
    db.init_app(app)


def create_all() -> None:
    """Create all of the tables in the database."""
    db.create_all()


def get_a_thing(thing_id: int) -> Thing:
    """
    Get data about a thing.

    Parameters
    ----------
    thing_id : int
        Unique identifier for the thing.

    Returns
    -------
    :class:`.Thing`
        Data about the thing.

    Raises
    ------
    IOError
        When there is a problem querying the database.
    :class:`NoSuchThing`
        When there is no such thing.

    """
    try:
        thing_data = db.session.query(DBThing).get(thing_id)
    except OperationalError as e:
        logger.debug('Encountered OperationalError: %s', e)
        raise IOError('Could not query database: %s' % e.detail) from e
    if thing_data is None:
        raise NoSuchThing(f'There is no {thing_id}')
    return Thing(id=thing_data.id,
                 name=thing_data.name,
                 created=thing_data.created)


def store_a_thing(the_thing: Thing) -> Thing:
    """
    Create a new record for a :class:`.Thing` in the database.

    Parameters
    ----------
    the_thing : :class:`.Thing`

    Raises
    ------
    IOError
        When there is a problem querying the database.
    RuntimeError
        When there is some other problem.
    """
    thing_data = DBThing(name=the_thing.name, created=the_thing.created)
    try:
        db.session.add(thing_data)
        db.session.commit()
    except Exception as e:
        raise RuntimeError('Ack! %s' % e) from e
    the_thing.id = thing_data.id
    return the_thing


def update_a_thing(the_thing: Thing) -> None:
    """
    Update the database with the latest :class:`.Thing`.

    Parameters
    ----------
    the_thing : :class:`.Thing`

    Raises
    ------
    IOError
        When there is a problem querying the database.
    RuntimeError
        When there is some other problem.
    """
    if not the_thing.id:
        raise RuntimeError('The thing has no id!')
    try:
        thing_data = db.session.query(DBThing).get(the_thing.id)
    except OperationalError as e:
        raise IOError('Could not query database: %s' % e.detail) from e
    if thing_data is None:
        raise RuntimeError('Cannot find the thing!')
    thing_data.name = the_thing.name
    db.session.add(thing_data)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError('Ack! %s' % e) from e

from sqlalchemy import BigInteger, Column, DateTime, Enum, \
    ForeignKey, Index, Integer, String, text
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy, Model


db = SQLAlchemy()


class Thing(db.Model):
    """Model for things."""

    __tablename__ = 'things'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created = Column(DateTime)


def get_a_thing(id: int) -> dict:
    """
    Get data about a thing.

    Parameters
    ----------
    id : int
        Unique identifier for the thing.

    Returns
    -------
    dict
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
        return
    return {
        'id': thing.id,
        'name': thing.name,
        'created': thing.created
    }

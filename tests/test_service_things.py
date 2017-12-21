"""Tests for :mod:`zero.services.things`."""

from unittest import TestCase, mock
from datetime import datetime
from zero.services import things
from zero.services.things import Thing
import sqlalchemy

from typing import Any

class TestThingGetter(TestCase):
    """The method :meth:`.get_a_thing` retrieves data about things."""

    def setUp(self) -> None:
        """Initialize an in-memory SQLite database."""
        from zero.services import things
        self.things = things
        app = mock.MagicMock(
            config={
                # 'SQLALCHEMY_DATABASE_URI': 'mysql://bob:dole@localhost/ack',
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
                'SQLALCHEMY_TRACK_MODIFICATIONS': False
            }, extensions={}, root_path=''
        )
        things.db.init_app(app)
        things.db.app = app
        things.db.create_all()

        self.data = dict(name='The first thing', created=datetime.now())
        self.thing = Thing(**self.data)
        things.db.session.add(self.thing)
        things.db.session.commit()

    def tearDown(self) -> None:
        """Clear the database and tear down all tables."""
        things.db.session.remove()
        things.db.drop_all()

    def test_get_a_thing_that_exists(self) -> None:
        """When the thing exists, returns data about the thing."""
        thing_data = things.get_a_thing(1)
        expected = dict(id=1, **self.data)
        if thing_data is not None:
           self.assertDictEqual(thing_data, expected)

    def test_get_a_thing_that_doesnt_exist(self) -> None:
        """When the thing doesn't exist, returns None."""
        self.assertIsNone(things.get_a_thing(2))

    @mock.patch('zero.services.things.db.session.query')
    def test_get_a_thing_when_database_is_unavailable(self, mock_query: Any) -> None:
        """When the database squawks, raises an IOError."""
        def raise_op_error(*args: str, **kwargs: str) -> None:
            raise sqlalchemy.exc.OperationalError('statement', {}, None)
        mock_query.side_effect = raise_op_error
        with self.assertRaises(IOError):
            things.get_a_thing(1)

"""Tests for :mod:`zero.services.things`."""

from unittest import TestCase, mock
from datetime import datetime
import sqlalchemy


class TestThingGetter(TestCase):
    """The method :meth:`.get_a_thing` retrieves data about things."""

    def setUp(self):
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
        self.things.db.init_app(app)
        self.things.db.app = app
        self.things.db.create_all()

        self.data = dict(name='The first thing', created=datetime.now())
        self.thing = self.things.Thing(**self.data)
        self.things.db.session.add(self.thing)
        self.things.db.session.commit()

    def tearDown(self):
        """Clear the database and tear down all tables."""
        self.things.db.session.remove()
        self.things.db.drop_all()

    def test_get_a_thing_that_exists(self):
        """When the thing exists, returns data about the thing."""
        thing_data = self.things.get_a_thing(1)
        expected = dict(id=1, **self.data)
        self.assertDictEqual(thing_data, expected)

    def test_get_a_thing_that_doesnt_exist(self):
        """When the thing doesn't exist, returns None."""
        self.assertIsNone(self.things.get_a_thing(2))

    @mock.patch('zero.services.things.db.session.query')
    def test_get_a_thing_when_database_is_unavailable(self, mock_query):
        """When the database squawks, raises an IOError."""
        def raise_op_error(*args, **kwargs):
            raise sqlalchemy.exc.OperationalError('statement', {}, None)
        mock_query.side_effect = raise_op_error
        with self.assertRaises(IOError):
            self.things.get_a_thing(1)

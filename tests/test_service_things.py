"""Tests for :mod:`zero.services.things`."""

from unittest import TestCase, mock
from datetime import datetime
import sqlalchemy
from zero.domain import Thing


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
        self.dbthing = self.things.DBThing(**self.data)
        self.things.db.session.add(self.dbthing)
        self.things.db.session.commit()

    def tearDown(self):
        """Clear the database and tear down all tables."""
        self.things.db.session.remove()
        self.things.db.drop_all()

    def test_get_a_thing_that_exists(self):
        """When the thing exists, returns a :class:`.Thing`."""
        thing = self.things.get_a_thing(1)
        self.assertIsInstance(thing, Thing)
        self.assertEqual(thing.id, 1)
        self.assertEqual(thing.name, self.data['name'])
        self.assertEqual(thing.created, self.data['created'])

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


class TestThingCreator(TestCase):
    """:func:`.store_a_thing` creates a new record in the database."""
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
        self.dbthing = self.things.DBThing(**self.data)
        self.things.db.session.add(self.dbthing)
        self.things.db.session.commit()

    def tearDown(self):
        """Clear the database and tear down all tables."""
        self.things.db.session.remove()
        self.things.db.drop_all()

    def test_store_a_thing(self):
        """A new row is added for the thing."""
        the_thing = Thing(name='The new thing', created=datetime.now())

        self.things.store_a_thing(the_thing)
        self.assertGreater(the_thing.id, 0, "Thing.id is updated with pk id")

        dbthing = self.things.db.session.query(self.things.DBThing)\
            .get(the_thing.id)

        self.assertEqual(dbthing.name, the_thing.name)


class TestThingUpdater(TestCase):
    """:func:`.update_a_thing` updates the db with :class:`.Thing` data."""

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
        self.dbthing = self.things.DBThing(**self.data)
        self.things.db.session.add(self.dbthing)
        self.things.db.session.commit()

    def tearDown(self):
        """Clear the database and tear down all tables."""
        self.things.db.session.remove()
        self.things.db.drop_all()

    def test_update_a_thing(self):
        """The db is updated with the current state of the :class:`.Thing`."""
        the_thing = Thing(id=self.dbthing.id, name='Whoops')
        self.things.update_a_thing(the_thing)

        dbthing = self.things.db.session.query(self.things.DBThing)\
            .get(self.dbthing.id)

        self.assertEqual(dbthing.name, the_thing.name)

    @mock.patch('zero.services.things.db.session.query')
    def test_operationalerror_is_handled(self, mock_query):
        """When the db raises an OperationalError, an IOError is raised."""
        the_thing = Thing(id=self.dbthing.id, name='Whoops')

        def raise_op_error(*args, **kwargs):
            raise sqlalchemy.exc.OperationalError('statement', {}, None)
        mock_query.side_effect = raise_op_error

        with self.assertRaises(IOError):
            self.things.update_a_thing(the_thing)

    def test_thing_really_does_not_exist(self):
        """If the :class:`.Thing` doesn't exist, a RuntimeError is raised."""
        the_thing = Thing(id=555, name='Whoops')    # Unlikely to exist.
        with self.assertRaises(RuntimeError):
            self.things.update_a_thing(the_thing)

    @mock.patch('zero.services.things.db.session.query')
    def test_thing_does_not_exist(self, mock_query):
        """If the :class:`.Thing` doesn't exist, a RuntimeError is raised."""
        the_thing = Thing(id=555, name='Whoops')    # Unlikely to exist.
        mock_query.return_value = mock.MagicMock(
            get=mock.MagicMock(return_value=None)
        )
        with self.assertRaises(RuntimeError):
            self.things.update_a_thing(the_thing)

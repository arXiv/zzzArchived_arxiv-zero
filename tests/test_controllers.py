"""Tests for :mod:`zero.controllers`."""

from unittest import TestCase, mock
from datetime import datetime
from zero.factory import create_web_app
from zero.domain import Baz, Thing
from zero.controllers import baz, things


class TestBazController(TestCase):
    """Test the :mod:`zero.controllers.baz` controller."""

    @mock.patch('zero.services.baz.retrieve_baz')
    def test_get_baz(self, mock_retrieve_baz):
        """:func:`.baz.get_baz` gets a Baz from the ``baz`` service."""
        mock_retrieve_baz.return_value = Baz(foo='bar', mukluk=1)

        response_data, status_code, headers = baz.get_baz(1)
        self.assertDictEqual(response_data, {'foo': 'bar', 'mukluk': 1})
        self.assertEqual(status_code, 200)

        mock_retrieve_baz.return_value = None
        response_data, status_code, headers = baz.get_baz(1)
        self.assertEqual(status_code, 404)

    @mock.patch('zero.services.baz.retrieve_baz')
    def test_baz_service_chokes(self, mock_retrieve_baz):
        """If the :mod:`.services.baz` chokes, returns 500."""
        mock_retrieve_baz.side_effect = IOError
        response_data, status_code, headers = baz.get_baz(1)
        self.assertEqual(status_code, 500)


class TestThingController(TestCase):
    """Test the :mod:`zero.controllers.things` controller."""

    @mock.patch('zero.services.things.get_a_thing')
    def test_get_thing(self, mock_get_a_thing):
        """:func:`.things.get_thing` gets a Thing from ``things`` service."""
        created = datetime.now()
        mock_get_a_thing.return_value = Thing(
            id=5,
            created=created,
            name='Thing!'
        )
        response_data, status_code, headers = things.get_thing(5)

        self.assertDictEqual(response_data,
                             {'name': 'Thing!', 'created': created, 'id': 5})
        self.assertEqual(status_code, 200)

        mock_get_a_thing.return_value = None
        response_data, status_code, headers = things.get_thing(5)
        self.assertEqual(status_code, 404)

    @mock.patch('zero.services.things.get_a_thing')
    def test_things_service_chokes(self, mock_get_a_thing):
        """If the :mod:`.services.baz` chokes, returns 500."""
        mock_get_a_thing.side_effect = IOError
        response_data, status_code, headers = things.get_thing(5)
        self.assertEqual(status_code, 500)

    @mock.patch('zero.services.things.store_a_thing')
    def test_create_a_thing(self, mock_store_a_thing):
        """Create a new :class:`.Thing` and store it."""
        thing_data = {'name': 'a new thing'}

        def _store(a_thing):
            a_thing.id = 5
            return a_thing
        mock_store_a_thing.side_effect = _store

        response_data, status_code, headers = things.create_a_thing(thing_data)
        self.assertEqual(status_code, 201, "Created")
        self.assertEqual(response_data['id'], 5)
        self.assertEqual(response_data['name'], 'a new thing')
        self.assertIn('Location', headers)

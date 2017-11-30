"""Tests for :mod:`zero.routes.external_api`."""

from unittest import TestCase, mock
from datetime import datetime
import json
import jsonschema
from zero.factory import create_web_app


class TestExternalAPIRoutes(TestCase):
    def setUp(self):
        self.app = create_web_app()
        self.client = self.app.test_client()

    @mock.patch('zero.services.baz.retrieve_baz')
    def test_get_baz(self, mock_retrieve_baz):
        """Endpoint /zero/baz/<int> returns JSON about a Baz."""
        with open('schema/baz.json') as f:
            schema = json.load(f)

        foo_data = {'id': 1, 'foo': 'bar', 'created': datetime.now()}
        mock_retrieve_baz.return_value = foo_data

        response = self.client.get('/zero/baz/1')

        expected_data = {'id': foo_data['id'], 'foo': foo_data['foo'],
                         'created': foo_data['created'].isoformat()}

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.data), expected_data)

        try:
            jsonschema.validate(json.loads(response.data), schema)
        except jsonschema.exceptions.SchemaError as e:
            self.fail(e)

    @mock.patch('zero.services.things.get_a_thing')
    def test_get_thing(self, mock_get_a_thing):
        """Endpoint /zero/thing/<int> returns JSON about a Thing."""
        with open('schema/thing.json') as f:
            schema = json.load(f)

        foo_data = {'id': 4, 'name': 'First thing', 'created': datetime.now()}
        mock_get_a_thing.return_value = foo_data

        response = self.client.get('/zero/thing/4')

        expected_data = {'id': foo_data['id'], 'name': foo_data['name'],
                         'created': foo_data['created'].isoformat()}

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.data), expected_data)

        try:
            jsonschema.validate(json.loads(response.data), schema)
        except jsonschema.exceptions.SchemaError as e:
            self.fail(e)

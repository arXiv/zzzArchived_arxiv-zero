"""Tests for :mod:`zero.routes.external_api`."""

from unittest import TestCase, mock
from datetime import datetime
import json
import jsonschema
from zero.factory import create_web_app
import jwt


def generate_token(app: object, claims: dict) -> str:
    """Helper function for generating a JWT."""
    secret = app.config.get('JWT_SECRET')
    return jwt.encode(claims, secret, algorithm='HS256')


class TestExternalAPIRoutes(TestCase):
    """Sample tests for external API routes."""

    def setUp(self):
        """Initialize the Flask application, and get a client for testing."""
        self.app = create_web_app()
        self.client = self.app.test_client()

    @mock.patch('zero.controllers.baz.get_baz')
    def test_get_baz(self, mock_get_baz):
        """Endpoint /zero/api/baz/<int> returns JSON about a Baz."""
        with open('schema/baz.json') as f:
            schema = json.load(f)

        foo_data = {'mukluk': 1, 'foo': 'bar'}
        mock_get_baz.return_value = foo_data, 200, {}

        response = self.client.get('/zero/api/baz/1')

        expected_data = {'mukluk': foo_data['mukluk'], 'foo': foo_data['foo']}

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.data), expected_data)

        try:
            jsonschema.validate(json.loads(response.data), schema)
        except jsonschema.exceptions.SchemaError as e:
            self.fail(e)

    @mock.patch('zero.controllers.things.get_thing')
    def test_get_thing(self, mock_get_thing):
        """Endpoint /zero/api/thing/<int> returns JSON about a Thing."""
        with open('schema/thing.json') as f:
            schema = json.load(f)

        foo_data = {'id': 4, 'name': 'First thing', 'created': datetime.now()}
        mock_get_thing.return_value = foo_data, 200, {}

        token = generate_token(self.app, {'scope': ['read:thing']})

        response = self.client.get('/zero/api/thing/4',
                                   headers={'Authorization': token})

        expected_data = {'id': foo_data['id'], 'name': foo_data['name'],
                         'created': foo_data['created'].isoformat()}

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.data), expected_data)

        try:
            jsonschema.validate(json.loads(response.data), schema)
        except jsonschema.exceptions.SchemaError as e:
            self.fail(e)

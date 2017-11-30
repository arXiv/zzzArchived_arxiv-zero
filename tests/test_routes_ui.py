"""Tests for :mod:`zero.routes.external_ui`."""

from unittest import TestCase, mock
from datetime import datetime
import jwt
from zero.factory import create_web_app


def generate_token(app: object, claims: dict) -> str:
    """Helper function for generating a JWT."""
    secret = app.config.get('JWT_SECRET')
    return jwt.encode(claims, secret, algorithm='HS256')


class TestUIRoutes(TestCase):
    """Sample tests for UI routes."""

    def setUp(self):
        """Initialize the Flask application, and get a client for testing."""
        self.app = create_web_app()
        self.client = self.app.test_client()

    @mock.patch('zero.services.baz.retrieve_baz')
    def test_get_baz(self, mock_retrieve_baz):
        """Endpoint /zero/ui/baz/<int> returns an HTML page about a Baz."""
        foo_data = {'id': 1, 'foo': 'bar', 'created': datetime.now()}
        mock_retrieve_baz.return_value = foo_data

        response = self.client.get('/zero/ui/baz/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

    @mock.patch('zero.services.things.get_a_thing')
    def test_get_thing(self, mock_get_a_thing):
        """Endpoint /zero/ui/thing/<int> returns HTML page about a Thing."""
        foo_data = {'id': 4, 'name': 'First thing', 'created': datetime.now()}
        mock_get_a_thing.return_value = foo_data

        token = generate_token(self.app, {'scope': ['read:thing']})

        response = self.client.get('/zero/ui/thing/4',
                                   headers={'Authorization': token})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

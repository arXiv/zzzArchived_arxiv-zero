"""Tests for :mod:`zero.routes.external_ui`."""

import os
from unittest import TestCase, mock
from datetime import datetime
from typing import Any, Optional

from flask import Flask

from arxiv.users.helpers import generate_token
from zero.factory import create_web_app
from .. import ui
from ..ui import READ_THING


class TestUIRoutes(TestCase):
    """Sample tests for UI routes."""

    def setUp(self) -> None:
        """Initialize the Flask application, and get a client for testing."""
        os.environ['JWT_SECRET'] = 'foosecret'
        self.app = create_web_app()
        self.client = self.app.test_client()

    @mock.patch(f'{ui.__name__}.controllers.get_baz')
    def test_get_baz(self, mock_get_baz: Any) -> None:
        """Endpoint /zero/ui/baz/<int> returns an HTML page about a Baz."""
        mock_get_baz.return_value = {'mukluk': 1, 'foo': 'bar'}, 200, {}

        response = self.client.get('/zero/ui/baz/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

    @mock.patch(f'{ui.__name__}.controllers.get_thing')
    def test_get_thing(self, mock_get_thing: Any) -> None:
        """Endpoint /zero/ui/thing/<int> returns HTML page about a Thing."""
        foo_data = {'id': 4, 'name': 'First thing', 'created': datetime.now()}
        mock_get_thing.return_value = foo_data, 200, {}

        token = generate_token('1234', 'foo@user.com', 'foouser', 
                               scope=[READ_THING])

        response = self.client.get('/zero/ui/thing/4',
                                   headers={'Authorization': token})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

"""Tests for :mod:`zero.routes.external_api`."""

import json
import os
from http import HTTPStatus
from typing import Any, Optional
from unittest import TestCase, mock
from datetime import datetime

import jsonschema
from flask import Flask

from arxiv.users.helpers import generate_token
from zero.factory import create_api_app
from ...services import things
from .. import external_api
from ..external_api import READ_THING, WRITE_THING


class TestExternalAPIRoutes(TestCase):
    """Sample tests for external API routes."""

    def setUp(self) -> None:
        """Initialize the Flask application, and get a client for testing."""
        os.environ['JWT_SECRET'] = 'foosecret'
        self.app = create_api_app()
        with self.app.app_context():
            things.create_all()
        self.client = self.app.test_client()

    @mock.patch(f'{external_api.__name__}.controllers.get_baz')
    def test_get_baz(self, mock_get_baz: Any) -> None:
        """Endpoint /zero/api/baz/<int> returns JSON about a Baz."""
        with open('schema/baz.json') as f:
            schema = json.load(f)

        foo_data = {'mukluk': 1, 'foo': 'bar'}
        mock_get_baz.return_value = foo_data, HTTPStatus.OK, {}

        response = self.client.get('/zero/api/baz/1')

        expected_data = {'mukluk': foo_data['mukluk'], 'foo': foo_data['foo']}

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)

        try:
            jsonschema.validate(json.loads(response.data), schema)
        except jsonschema.exceptions.SchemaError as e:
            self.fail(e)

    @mock.patch(f'{external_api.__name__}.controllers.get_thing')
    def test_get_thing(self, mock_get_thing: Any) -> None:
        """Endpoint /zero/api/thing/<int> returns JSON about a Thing."""
        with open('schema/thing.json') as f:
            schema = json.load(f)

        foo_data = {'id': 4, 'name': 'First thing', 'created': datetime.now()}
        mock_get_thing.return_value = foo_data, HTTPStatus.OK, {}

        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[READ_THING])

        response = self.client.get('/zero/api/thing/4',
                                   headers={'Authorization': token})

        expected_data = {
            'id': foo_data['id'], 'name': foo_data['name'],
            'created': foo_data['created'].isoformat() # type: ignore
        }

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)

        try:
            jsonschema.validate(json.loads(response.data), schema)
        except jsonschema.exceptions.SchemaError as e:
            self.fail(e)

    @mock.patch(f'{external_api.__name__}.controllers.create_a_thing')
    def test_create_thing(self, mock_create_a_thing: Any) -> None:
        """POST to endpoint /zero/api/thing creates and stores a Thing."""
        foo_data = {'name': 'A New Thing'}
        return_data = {'name': 'A New Thing',
                       'id': 25,
                       'created': datetime.now(),
                       'url': '/zero/api/thing/25'}
        headers = {'Location': '/zero/api/thing/25'}
        mock_create_a_thing.return_value = \
            return_data, HTTPStatus.CREATED, headers

        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[READ_THING, WRITE_THING])

        response = self.client.post('/zero/api/thing',
                                    data=json.dumps(foo_data),
                                    headers={'Authorization': token},
                                    content_type='application/json')

        expected_data = {
            'id': return_data['id'], 'name': return_data['name'],
            'created': return_data['created'].isoformat(), #type: ignore
            'url': return_data['url']
        }

        self.assertEqual(response.status_code, HTTPStatus.CREATED, "Created")
        self.assertDictEqual(json.loads(response.data), expected_data)

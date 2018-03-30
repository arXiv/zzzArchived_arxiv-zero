"""Tests for :mod:`.middleware`."""

from unittest import TestCase, mock
from flask import Flask

import sys
from arxiv.base import middleware

from zero.middleware import auth


class TestExampleAuthMiddleware(TestCase):
    """Test :func:`.auth.ExampleAuthMiddleware`."""

    def setUp(self):
        """Define a minimal request environment."""
        self.environ = {
            'SERVER_NAME': 'fooserver',
            'SERVER_PORT': '123',
            'wsgi.url_scheme': 'http',
            'REQUEST_METHOD': 'HEAD'
        }

    def test_authorization_header_is_missing(self):
        """Request does not include Authorization header."""
        foo = mock.MagicMock()
        wrapped = auth.ExampleAuthMiddleware(foo)
        wrapped(self.environ, mock.MagicMock())
        environ, _ = foo.call_args[0]

        self.assertIsNone(environ['auth'],
                          "auth parameter passed to app should be None")

    def test_authorization_header_is_garbage(self):
        """Request includes a garbled or forged auth header."""
        self.environ['HTTP_AUTHORIZATION'] = 'garbage'
        foo = mock.MagicMock()
        wrapped = auth.ExampleAuthMiddleware(foo)
        wrapped(self.environ, mock.MagicMock())
        environ, _ = foo.call_args[0]

        self.assertIsNone(environ['auth'],
                          "auth parameter passed to app should be None")

    @mock.patch('zero.middleware.auth.config')
    def test_authorization_header_is_valid(self, mock_config):
        """A valid JWT is included in the Authorization header."""
        import jwt
        claims = {'scope': ['fooscope'], 'user': 'foouser'}
        mock_config.JWT_SECRET = 'barsecret'
        token = jwt.encode(claims, 'barsecret', algorithm='HS256')
        self.environ['HTTP_AUTHORIZATION'] = token

        foo = mock.MagicMock()
        wrapped = auth.ExampleAuthMiddleware(foo)
        wrapped(self.environ, mock.MagicMock())
        environ, _ = foo.call_args[0]

        self.assertEqual(environ['auth']['scope'], ['fooscope'],
                         "auth scope from JWT should be passed to app")
        self.assertEqual(environ['auth']['user'], 'foouser',
                         "auth user from JWT should be passed to app")

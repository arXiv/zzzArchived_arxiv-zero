"""Tests for :mod:`zero.services.foo`."""

from unittest import mock, TestCase
from functools import partial
import json
import requests
from zero.services import baz

from typing import Any, Optional

class TestBazServiceStatus(TestCase):
    """The method :meth:`.status` indicates the status of the Baz service."""

    @mock.patch('zero.services.baz.requests.Session')
    def test_status_returns_true_when_remote_is_ok(self, mock_session: Any) -> None:
        """If the remote baz service is OK, :meth:`.status` returns True."""
        mock_get_response = mock.MagicMock(status_code=200, ok=True)
        mock_get = mock.MagicMock(return_value=mock_get_response)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        self.assertTrue(bazSession.status())

    @mock.patch('zero.services.baz.requests.Session')
    def test_status_returns_false_when_remote_is_not_ok(self, mock_session: Any) -> None:
        """If the remote baz service isn't ok :meth:`.status` returns False."""
        mock_get_response = mock.MagicMock(status_code=503, ok=False)
        mock_get = mock.MagicMock(return_value=mock_get_response)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        self.assertFalse(bazSession.status())

    @mock.patch('zero.services.baz.requests.Session')
    def test_status_returns_false_when_an_error_occurs(self, mock_session: Any) -> None:
        """If there is a problem calling baz :meth:`.status` returns False."""
        mock_get = mock.MagicMock(side_effect=requests.exceptions.HTTPError)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        self.assertFalse(bazSession.status())


class TestBazServiceRetrieve(TestCase):
    """The method :meth:`.retrieve_baz` is for getting baz."""

    @mock.patch('zero.services.baz.requests.Session')
    def test_returns_none_when_not_found(self, mock_session: Any) -> None:
        """If there is no such baz, returns None."""
        mock_get_response = mock.MagicMock(status_code=404, ok=False)
        mock_get = mock.MagicMock(return_value=mock_get_response)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        self.assertIsNone(bazSession.retrieve_baz(4))

    @mock.patch('zero.services.baz.requests.Session')
    def test_returns_dict_when_valid_json_returned(self, mock_session: Any) -> None:
        """If there is a baz, returns the data returned by baz service."""
        mock_json = mock.MagicMock(return_value={'bazdata': 'foo'})
        mock_get_response = mock.MagicMock(status_code=200, ok=True,
                                           json=mock_json)
        mock_get = mock.MagicMock(return_value=mock_get_response)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        bazRetrieval = bazSession.retrieve_baz(4)
        self.assertIsNotNone(bazRetrieval)
        if bazRetrieval is not None:
            self.assertDictEqual(bazRetrieval, {'bazdata': 'foo'})

    @mock.patch('zero.services.baz.requests.Session')
    def test_raises_ioerror_when_status_not_ok(self, mock_session: Any) -> None:
        """If the the baz service returns a bad status, raises IOError."""
        mock_get_response = mock.MagicMock(status_code=500, ok=False)
        mock_get = mock.MagicMock(return_value=mock_get_response)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        with self.assertRaises(IOError):
            bazSession.retrieve_baz(4)

    @mock.patch('zero.services.baz.requests.Session')
    def test_raises_ioerror_when_data_is_bad(self, mock_session: Any) -> None:
        """If the the baz service retrieves non-JSON data, raises IOError."""
        def raise_decoderror() -> None:
            raise json.decoder.JSONDecodeError('msg', 'doc', 0)

        mock_json = mock.MagicMock(side_effect=raise_decoderror)
        mock_get_response = mock.MagicMock(status_code=200, ok=True,
                                           json=mock_json)
        mock_get = mock.MagicMock(return_value=mock_get_response)
        mock_session_instance = mock.MagicMock()
        type(mock_session_instance).get = mock_get
        mock_session.return_value = mock_session_instance

        bazSession = baz.BazServiceSession('foo')
        with self.assertRaises(IOError):
            bazSession.retrieve_baz(4)

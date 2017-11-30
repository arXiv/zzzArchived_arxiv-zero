"""The baz service provides data about bazs."""
import json
from urllib.parse import urlparse, urljoin
from urllib3 import Retry
import requests
import werkzeug

from zero.context import get_application_config, get_application_global
from zero import logging

logger = logging.getLogger(__name__)


class BazServiceSession(object):
    """
    Preserves state re:baz that must persist throughout the request context.

    This could be an HTTP session, database connection, etc.
    """

    bazcave = 'https://asdf.com'

    def __init__(self, baz_param: str):
        """Create a new HTTP session."""
        self.baz_param = baz_param
        self._session = requests.Session()
        self._adapter = requests.adapters.HTTPAdapter(max_retries=2)
        self._session.mount('http://', self._adapter)
        logger.debug('New BazServiceSession with baz_param = %s', baz_param)

    def status(self) -> bool:
        """Check the availability of the Baz service."""
        try:
            response = self._session.get(urljoin(self.bazcave, '/health'))
        except requests.exceptions.RequestException:
            return False
        if not response.ok:
            return False
        return True

    def retrieve_baz(self, baz_id: int) -> dict:
        """
        Go get a baz and bring it back.

        Parameters
        ----------
        baz_id : int
            The PK id of the baz of interest.

        Return
        ------
        dict
            Data about the baz.

        Raises
        ------
        IOError
            If there is a problem getting the baz.
        """
        logger.debug('Retrieve a baz with id = %i', baz_id)
        response = self._session.get(urljoin(self.bazcave,
                                             '/baz/%i' % baz_id))
        if not response.ok:
            logger.debug('Baz responded with status %i', response.status_code)
            if response.status_code == requests.codes['-o-']:
                return None
            raise IOError('Could not get baz: %i' % response.status_code)
        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            logger.debug('Baz response could not be decoded')
            raise IOError('Could not read the baz') from e
        logger.debug('Got a baz with foo: %s', data.get('foo'))
        return data


def init_app(app: werkzeug.local.LocalProxy=None):
    """
    Set required configuration defaults for the application.

    Parameters
    ----------
    app : :class:`werkzeug.local.LocalProxy`
    """
    app.config.setdefault('BAZ_PARAM', 'baz')


def get_session(app: werkzeug.local.LocalProxy=None) -> BazServiceSession:
    """
    Create a new Baz session.

    Parameters
    ----------
    app : :class:`werkzeug.local.LocalProxy`

    Return
    ------
    :class:`.BazServiceSession`
    """
    config = get_application_config(app)
    baz_param = config['BAZ_PARAM']
    return BazServiceSession(baz_param)


def current_session(app: werkzeug.local.LocalProxy=None) -> BazServiceSession:
    """
    Get the current Baz session for this context (if there is one).

    Parameters
    ----------
    app : :class:`werkzeug.local.LocalProxy`

    Return
    ------
    :class:`.BazServiceSession`
    """
    g = get_application_global()
    if g:
        if 'baz' not in g:
            g.baz = get_session(app)
        return g.baz
    return get_session(app)


def retrieve_baz(baz_id: int) -> dict:
    """
    Go get a baz and bring it back.

    Parameters
    ----------
    baz_id : int
        The PK id of the baz of interest.

    Return
    ------
    dict
        Data about the baz.

    Raises
    ------
    IOError
        If there is a problem getting the baz.
    """
    return current_session().retrieve_baz(baz_id)

"""Example middleware for decoding encrypted JWTs on each request."""

from typing import Callable, Iterable, Tuple
import jwt
from zero import config
from arxiv.base.middleware import BaseMiddleware


class ExampleAuthMiddleware(BaseMiddleware):
    """
    An example of middleware to handle auth information on requests.

    Before the request is handled by the application, the ``Authorization``
    header is parsed for an encrypted JWT. If successfully decrypted,
    information about the user and their authorization scope is attached
    to the request.

    This can be accessed in the application via
    ``flask.request.environ['auth']``.  If Authorization header was not
    included, or if the JWT could not be decrypted, then that value will be
    ``None``.
    """

    def before(self, environ: dict, start_response: Callable) \
            -> Tuple[dict, Callable]:
        """Parse the ``Authorization`` header in the response."""
        auth_header = environ.get('HTTP_AUTHORIZATION')
        environ['auth'] = None
        if not auth_header:
            return environ, start_response
        try:
            decoded = jwt.decode(auth_header, config.JWT_SECRET,
                                 algorithms=['HS256'])
        except jwt.exceptions.DecodeError:  # type: ignore
            return environ, start_response

        environ['auth'] = {
            'scope': decoded.get('scope', []),
            'user': decoded.get('user')
        }
        return environ, start_response

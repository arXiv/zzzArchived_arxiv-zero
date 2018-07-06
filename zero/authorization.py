"""A minimal example of scope-based authorization."""

from functools import wraps
from flask import request, current_app, jsonify
import jwt

from typing import Any, Callable, Dict, Tuple
from werkzeug.exceptions import Forbidden, Unauthorized


# TODO: this will be replaced by the arxiv.users package.
def scoped(scope: str) -> Callable[[Any], Any]:
    """Generate a decorator to enforce scope authorization."""
    def protector(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """Decorator that provides scope enforcement."""
        @wraps(func)
        def wrapper(*args: str, **kwargs: str) -> Any:
            """Check the authorization token before executing the method."""
            if not request.environ['auth']:
                raise Unauthorized('Authentication required for this resource')
            if scope not in request.environ['auth']['scope']:
                raise Forbidden('Insufficient privileges to access resource')
            return func(*args, **kwargs)    # type: ignore
        return wrapper
    return protector

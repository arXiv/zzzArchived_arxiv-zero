"""Controllers for operations on :class:`.Baz`."""

from typing import Tuple, Optional, Dict, Any, IO, Union
from http import HTTPStatus

from flask import url_for
from werkzeug.exceptions import NotFound, InternalServerError

from ..services import baz
from ..domain import Baz

NO_BAZ = 'could not find the baz'
BAZ_WONT_GO = 'could not get the baz'

Body = Union[Dict[str, Any], IO]
Headers = Dict[str, str]
ResponseData = Tuple[Body, HTTPStatus, Headers]


def get_baz(baz_id: int) -> ResponseData:
    """
    Retrieve a baz from the Baz service.

    Parameters
    ----------
    baz_id : int
        The unique identifier for the baz in question.
    Returns
    -------
    dict
        Some interesting information about the baz.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.

    """
    baz_data: Dict[str, Any]
    baz_service = baz.BazService.current_session()
    try:
        the_baz: Baz = baz_service.retrieve_baz(baz_id)
    except baz.NoBaz as e:
        raise NotFound('No such baz') from e
    except IOError:
        raise InternalServerError(BAZ_WONT_GO) from e

    baz_data = {'foo': the_baz.foo, 'mukluk': the_baz.mukluk}
    return baz_data, HTTPStatus.OK, {}
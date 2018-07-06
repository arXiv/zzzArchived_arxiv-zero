"""Handles all baz-related requests."""

from typing import Tuple, Optional, Dict, Any
from werkzeug.exceptions import NotFound, InternalServerError
from arxiv import status
from zero.services import baz
from zero.domain import Baz

NO_BAZ = 'could not find the baz'
BAZ_WONT_GO = 'could not get the baz'


def get_baz(baz_id: int) -> Tuple[Optional[dict], int, dict]:
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
    try:
        the_baz: Baz = baz.retrieve_baz(baz_id)
        if the_baz is None:
            raise NotFound(NO_BAZ)
        else:
            status_code = status.HTTP_200_OK
            baz_data = {'foo': the_baz.foo, 'mukluk': the_baz.mukluk}
    except IOError:
        raise InternalServerError(BAZ_WONT_GO)
    return baz_data, status_code, {}

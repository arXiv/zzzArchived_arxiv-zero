"""Handles all thing-related requests."""

from typing import Tuple
from zero import status
from zero.services import things
from typing import Optional

def get_thing(thing_id: int) -> Tuple[Optional[dict], int, dict]:
    """
    Retrieve a thing from the Things service.

    Parameters
    ----------
    thing_id : int
        The unique identifier for the thing in question.

    Returns
    -------
    dict
        Some interesting information about the thing.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.
    """
    try:
        response_data = things.get_a_thing(thing_id)
        if response_data is None:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_200_OK
    except IOError:
        response_data = {'reason': 'could not get the thing'}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response_data, status_code, {}

"""Handles all thing-related requests."""

from typing import Tuple, Optional
from zero import status
from zero.services import things
from zero.domain import Thing


NO_SUCH_THING = {'reason': 'there is no thing'}
THING_WONT_COME = {'reason': 'could not get the thing'}


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
        thing: Thing = things.get_a_thing(thing_id)
        if thing is None:
            status_code = status.HTTP_404_NOT_FOUND
            response_data = NO_SUCH_THING
        else:
            status_code = status.HTTP_200_OK
            response_data = {'name': thing.name, 'created': thing.created}
    except IOError:
        response_data = THING_WONT_COME
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response_data, status_code, {}

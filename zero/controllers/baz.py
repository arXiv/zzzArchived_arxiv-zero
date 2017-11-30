"""Handles all baz-related requests."""

from zero import status
from zero.services import baz


def get_baz(baz_id: int) -> dict:
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
    try:
        baz_data = baz.retrieve_baz(baz_id)
        if baz_data is None:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_200_OK
    except IOError:
        baz_data = {'reason': 'could not get the baz'}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return baz_data, status_code, {}

"""Handles all thing-related requests."""

from typing import Tuple, Optional
from zero import status
from zero.services import things
from zero.domain import Thing
from zero.tasks import mutate_a_thing, check_mutation_status

from flask import url_for


NO_SUCH_THING = {'reason': 'there is no thing'}
THING_WONT_COME = {'reason': 'could not get the thing'}
ACCEPTED = {'reason': 'mutation in progress'}
INVALID_TASK_ID = {'reason': 'invalid task id'}
TASK_DOES_NOT_EXIST = {'reason': 'task not found'}
TASK_IN_PROGRESS = {'status': 'in progress'}
TASK_FAILED = {'status': 'failed'}
TASK_COMPLETE = {'status': 'complete'}

Response = Tuple[Optional[dict], int, dict]


def get_thing(thing_id: int) -> Response:
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


def start_mutating_a_thing(thing_id: int) -> Response:
    """
    Start mutating a :class:`.Thing`.

    Parameters
    ----------
    thing_id : int

    Returns
    -------
    dict
        Some data (you know).
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.
    """
    result = mutate_a_thing.delay(thing_id)
    headers = {'Location': url_for('zero.task_status', task_id=result.task_id)}
    return ACCEPTED, status.HTTP_202_ACCEPTED, headers


def mutation_status(task_id: str) -> Response:
    """
    Check the status of a mutation process.

    Parameters
    ----------
    task_id : str
        The ID of the mutation task.

    Returns
    -------
    dict
        Some data (you know).
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.
    """
    try:
        task_status, result = check_mutation_status(task_id)
    except ValueError as e:
        return INVALID_TASK_ID, status.HTTP_400_BAD_REQUEST, {}
    if task_status == 'PENDING':
        return TASK_DOES_NOT_EXIST, status.HTTP_404_NOT_FOUND, {}
    elif task_status in ['SENT', 'STARTED', 'RETRY']:
        return TASK_IN_PROGRESS, status.HTTP_200_OK, {}
    elif task_status == 'FAILURE':
        reason = TASK_FAILED
        reason.update({'reason': str(result)})
        return reason, status.HTTP_200_OK, {}
    elif task_status == 'SUCCESS':
        reason = TASK_COMPLETE
        reason.update({'result': result})
        headers = {'Location': url_for('zero.read_thing',
                                       thing_id=result['thing_id'])}
        return TASK_COMPLETE, status.HTTP_303_SEE_OTHER, headers
    return TASK_DOES_NOT_EXIST, status.HTTP_404_NOT_FOUND, {}

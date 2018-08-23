"""Handles all thing-related requests."""

from typing import Tuple, Optional, Any, Dict
from datetime import datetime
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError
from arxiv import status
from zero.services import things
from zero.domain import Thing
from zero.tasks import mutate_a_thing, check_mutation_status

from zero.shared import url_for


NO_SUCH_THING = 'there is no thing'
THING_WONT_COME = 'could not get the thing'
CANT_CREATE_THING = 'could not create the thing'
MISSING_NAME = 'a thing needs a name'
ACCEPTED = 'mutation in progress'
INVALID_TASK_ID = 'invalid task id'
TASK_DOES_NOT_EXIST = 'task not found'
TASK_IN_PROGRESS = {'status': 'in progress'}
TASK_FAILED = {'status': 'failed'}
TASK_COMPLETE = {'status': 'complete'}


Response = Tuple[Dict[str, Any], int, Dict[str, Any]]


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
    response_data: Dict[str, Any]
    try:
        thing: Optional[Thing] = things.get_a_thing(thing_id)
    except IOError:
        raise InternalServerError(THING_WONT_COME)

    if thing is None:
        raise NotFound(NO_SUCH_THING)

    status_code = status.HTTP_200_OK
    response_data = {
        'id': thing.id,
        'name': thing.name,
        'created': thing.created
    }
    return response_data, status_code, {}


def create_a_thing(thing_data: dict) -> Response:
    """
    Create a new :class:`.Thing`.

    Parameters
    ----------
    thing_data : dict
        Data used to create a new :class:`.Thing`.

    Returns
    -------
    dict
        Some data.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.
    """
    name = thing_data.get('name')
    headers = {}
    response_data: Dict[str, Any]
    if not name or not isinstance(name, str):
        raise BadRequest(MISSING_NAME)

    thing = Thing(name=name, created=datetime.now())      # type: ignore
    try:
        things.store_a_thing(thing)
    except RuntimeError as e:
        raise InternalServerError(CANT_CREATE_THING)

    status_code = status.HTTP_201_CREATED
    thing_url = url_for('external_api.read_thing',  # type: ignore
                        thing_id=thing.id)
    response_data = {
        'id': thing.id,
        'name': thing.name,
        'created': thing.created,
        'url': thing_url
    }
    headers['Location'] = thing_url
    return response_data, status_code, headers


def start_mutating_a_thing(thing_id: int) -> Response:
    """
    Start mutating a :class:`.Thing`.

    Parameters
    ----------
    thing_id : int

    Returns
    -------
    dict
        Some data.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.
    """
    result = mutate_a_thing.delay(thing_id)
    headers = {'Location': url_for('external_api.mutation_status',
                                   task_id=result.task_id)}
    return {'reason': ACCEPTED}, status.HTTP_202_ACCEPTED, headers


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
        Some data.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.
    """
    try:
        task_status, result = check_mutation_status(task_id)
    except ValueError as e:
        raise BadRequest(INVALID_TASK_ID)
    if task_status == 'PENDING':
        raise NotFound(TASK_DOES_NOT_EXIST)
    elif task_status in ['SENT', 'STARTED', 'RETRY']:
        return TASK_IN_PROGRESS, status.HTTP_200_OK, {}
    elif task_status == 'FAILURE':
        reason = TASK_FAILED
        reason.update({'reason': str(result)})
        return reason, status.HTTP_200_OK, {}
    elif task_status == 'SUCCESS':
        reason = TASK_COMPLETE
        reason.update({'result': result})
        headers = {'Location': url_for('external_api.read_thing',
                                       thing_id=result['thing_id'])}
        return TASK_COMPLETE, status.HTTP_303_SEE_OTHER, headers
    raise NotFound(TASK_DOES_NOT_EXIST)

"""Handles all thing-related requests."""

import io
from typing import Tuple, Optional, Any, Dict, Union, IO
from http import HTTPStatus
from datetime import datetime

from werkzeug.exceptions import NotFound, BadRequest, InternalServerError
from arxiv import status
from arxiv.base import logging
from ..services import things
from ..domain import Thing
from ..tasks import mutate_a_thing, check_mutation_status, NoSuchTask

from flask import url_for

Body = Union[Dict[str, Any], IO]
Headers = Dict[str, str]
ResponseData = Tuple[Body, HTTPStatus, Headers]

logger = logging.getLogger(__name__)

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


def get_thing(thing_id: int) -> ResponseData:
    """
    Retrieve a thing.

    Parameters
    ----------
    thing_id : int
        The unique identifier for the thing in question.
    Returns
    -------
    io.BytesIO
        Some interesting information about the thing.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.

    """
    logger.debug('Request to get a thing: %s', thing_id)
    try:
        thing = things.get_a_thing(thing_id)
    except things.NoSuchThing as e:
        logger.debug('No such thing: %s', e)
        raise NotFound(NO_SUCH_THING) from e
    except IOError as e:
        logger.debug('Encountered IOError: %s', e)
        raise InternalServerError(THING_WONT_COME) from e
    logger.debug('Got the thing: %s', thing)
    return io.BytesIO(thing.name.encode('utf-8')), HTTPStatus.OK, {}


def get_thing_description(thing_id: int) -> ResponseData:
    """
    Retrieve description of a thing.

    Parameters
    ----------
    thing_id : int
        The unique identifier for the thing in question.
    Returns
    -------
    dict
        Summary information about the thing.
    int
        An HTTP status code.
    dict
        Some extra headers to add to the response.

    """
    logger.debug('Request to get a thing: %s', thing_id)
    try:
        thing = things.get_a_thing(thing_id)
    except things.NoSuchThing as e:
        logger.debug('No such thing: %s', e)
        raise NotFound(NO_SUCH_THING) from e
    except IOError as e:
        logger.debug('Encountered IOError: %s', e)
        raise InternalServerError(THING_WONT_COME) from e
    logger.debug('Got the thing: %s', thing)
    thing_url = url_for('external_api.read_thing', thing_id=thing.id)
    response_data = {
        'id': thing.id,
        'name': thing.name,
        'created': thing.created,
        'url': thing_url
    }
    return response_data, HTTPStatus.OK, {}


def create_a_thing(thing_data: dict) -> ResponseData:
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
    response_data: Dict[str, Any]
    if not name or not isinstance(name, str):
        raise BadRequest(MISSING_NAME)

    thing = Thing(name=name, created=datetime.now())
    try:
        things.store_a_thing(thing)
    except RuntimeError as e:
        raise InternalServerError(CANT_CREATE_THING) from e

    if not thing.is_persisted:
        raise InternalServerError('Thing not persisted')

    thing_url = url_for('external_api.read_thing', thing_id=thing.id)
    response_data = {
        'id': thing.id,
        'name': thing.name,
        'created': thing.created,
        'url': thing_url
    }
    return response_data, HTTPStatus.CREATED, {'Location': thing_url}


def start_mutating_a_thing(thing_id: int) -> ResponseData:
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
    stat_url = url_for('external_api.mutation_status', task_id=result.task_id)
    return {'reason': ACCEPTED}, HTTPStatus.ACCEPTED, {'Location': stat_url}


def mutation_status(task_id: str) -> ResponseData:
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
        task = check_mutation_status(task_id)
    except ValueError as e:
        raise BadRequest(INVALID_TASK_ID) from e
    except NoSuchTask as e:
        raise NotFound(TASK_DOES_NOT_EXIST) from e

    status_code = HTTPStatus.OK
    response_data: Dict[str, Any] = {}
    headers: Dict[str, Any] = {}

    logger.debug('task status is %s', task.status)
    if task.is_in_progress:
        logger.debug('task is in progress')
        response_data.update(TASK_IN_PROGRESS)
    elif task.is_failed:
        logger.debug('task has failed')
        response_data.update(TASK_FAILED)
        response_data.update({'reason': str(task.result)})
    elif task.is_complete:
        logger.debug('task is complete')
        if task.result is None:
            raise InternalServerError('Task is complete but result is None')
        response_data.update(TASK_COMPLETE)
        response_data.update({'result': task.result})
        thing_url = url_for('external_api.read_thing',
                            thing_id=task.result['thing_id'])
        headers.update({'Location': thing_url})
        status_code = HTTPStatus.SEE_OTHER
    return response_data, status_code, headers

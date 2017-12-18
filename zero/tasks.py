"""Asynchronous tasks."""

import time
from celery import shared_task
from celery.result import AsyncResult
from celery.signals import after_task_publish
from celery import current_app
from zero.services import things
from zero.process import mutate
from zero.domain import Thing


@shared_task
def mutate_a_thing(thing_id: int, with_sleep: int = 5) -> int:
    """
    Perform some expen$ive mutations on a :class:`.Thing`.

    Parameters
    ----------
    thing_id : int

    Returns
    -------
    int
        The number of characters in :prop:`.Thing.name` after mutation.
    """
    a_thing: Thing = things.get_a_thing(thing_id)
    mutate.add_some_one_to_the_thing(a_thing)
    time.sleep(with_sleep)
    things.update_a_thing(a_thing)
    return {'thing_id': thing_id, 'result': len(a_thing.name)}


def check_mutation_status(task_id: str) -> str:
    """
    Check the status of a mutation task.

    Parameters
    ----------
    task_id : str
        A mutation task ID.

    Returns
    -------
    str
        Status.
    """
    if not isinstance(task_id, str):
        raise ValueError('task_id must be string, not %s' % type(task_id))
    task = AsyncResult(task_id)
    if task.status in ['SUCCESS', 'FAILED']:
        result = task.result
    else:
        result = None
    return task.status, result


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, body=None, **kwargs):
    """Set state to SENT, so that we can tell whether a task exists."""
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(headers['id'], None, "SENT")

"""Asynchronous tasks."""

import time
from celery import shared_task
from celery.result import AsyncResult
from zero.services import things
from zero.process import mutate
from zero.domain import Thing


@shared_task
def mutate_a_thing(thing_id: int) -> int:
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
    time.sleep(10)
    things.update_a_thing(a_thing)
    return len(a_thing.name)


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
    if task.status in ['PENDING', 'FAILED']:
        result = task.result
    else:
        result = None
    return task.status, result

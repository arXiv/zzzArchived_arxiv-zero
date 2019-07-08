"""Asynchronous tasks."""

import time
from typing import Optional, Dict, Any, Tuple, Callable

from celery import shared_task
from celery.result import AsyncResult
from celery.signals import after_task_publish
from celery import current_app

from .services import things
from .domain import Thing, Task
from .process import mutate


STATE_MAP = {'SENT': Task.Status.IN_PROGRESS,
             'STARTED': Task.Status.IN_PROGRESS,
             'RETRY': Task.Status.IN_PROGRESS,
             'FAILURE': Task.Status.FAILURE,
             'SUCCESS': Task.Status.SUCCESS}
"""Maps Celery task states to :class:`.Task.Status`."""


class NoSuchTask(Exception):
    """An operation on a non-existant task was attempted."""


@shared_task
def mutate_a_thing(thing_id: int, with_sleep: int = 5) -> Dict[str, Any]:
    """
    Perform some expen$ive mutations on a :class:`.Thing`.

    Parameters
    ----------
    thing_id : int

    Returns
    -------
    int
        The number of characters in :attr:`.Thing.name` after mutation.
    """
    a_thing: Optional[Thing] = things.get_a_thing(thing_id)
    if a_thing is None:
        raise RuntimeError('No such thing! %s' % thing_id)
    mutate.add_some_one_to_the_thing(a_thing)
    time.sleep(with_sleep)
    things.update_a_thing(a_thing)
    return {'thing_id': thing_id, 'result': len(a_thing.name)}


def check_mutation_status(task_id: str) -> Task:
    """
    Check the status of a mutation task.

    Parameters
    ----------
    task_id : str
        A mutation task ID.

    Returns
    -------
    :class:`.Task`

    """
    if not isinstance(task_id, str):
        raise ValueError('task_id must be string, not %s' % type(task_id))

    celery_task = AsyncResult(task_id)

    # Since we are explicitly setting the state to SENT upon publication of the
    # task (see ``update_sent_state()``), any AsyncResult in ``PENDING`` refers
    # to a non-existant task.
    if celery_task.status == 'PENDING':
        raise NoSuchTask(f'No such task: {task_id}')

    task = Task(task_id=task_id, status=STATE_MAP[celery_task.status])
    if task.is_complete:
        task.result = celery_task.result
    return task


@after_task_publish.connect
def update_sent_state(sender: Optional[Callable] = None,
                      headers: Optional[dict] = None, body: Any = None,
                      **kwargs: Any) -> None:
    """Set state to SENT, so that we can tell whether a task exists."""
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    if headers is not None:
        backend.store_result(headers['id'], None, "SENT")

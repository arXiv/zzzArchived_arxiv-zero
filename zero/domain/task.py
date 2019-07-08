"""Describes an asynchronous task."""

from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


@dataclass
class Task:

    class Status(Enum):
        IN_PROGRESS = 'IN_PROGRESS'
        FAILURE = 'FAILURE'
        SUCCESS = 'SUCCESS'

    task_id: str
    """Identifier for the task."""

    status: Status
    """Current status of the task."""

    result: Optional[Dict[str, Any]] = field(default=None)
    """The final result of the task, if there was one."""

    @property
    def is_in_progress(self) -> bool:
        return bool(self.status is Task.Status.IN_PROGRESS)

    @property
    def is_failed(self) -> bool:
        return bool(self.status is Task.Status.FAILURE)

    @property
    def is_complete(self) -> bool:
        return bool(self.status in (Task.Status.SUCCESS, Task.Status.FAILURE))

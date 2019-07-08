"""Provides concepts about things."""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field

from pytz import UTC


def _now() -> datetime:
    """Get the current datetime in UTC."""
    return datetime.now(UTC)


@dataclass
class Thing:
    """Description of a thing."""

    name: str
    """The name of the thing."""

    id: Optional[int] = field(default=None)
    """
    The unique identifier for a thing.
    
    If ``id`` is ``None``, the thing has not been persisted.
    """

    created: datetime = field(default_factory=_now)
    """The datetime when the thing was created."""

    def is_persisted(self) -> bool:
        """Determine whether or not the thing has been persisted."""
        return bool(self.id is not None)

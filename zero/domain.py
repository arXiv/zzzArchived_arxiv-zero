"""Describes the data that will be passed around inside of this service."""

from datetime import datetime
from typing import Type, Any, Optional

from dataclasses import dataclass, field
from dataclasses import asdict as _asdict


@dataclass
class Baz:
    """Baz est ut mi semper mattis non eget tellus."""

    foo: str
    """Foo a tellus sit amet purus pharetra gravida vulputate ut purus."""

    mukluk: int
    """A soft boot, traditionally made of reindeer skin or sealskin."""


@dataclass
class Thing:
    """
    A thing in itself.

    The attention will tend toward the species either in such a way that it
    would not pass beyond so as to attend to the object, or in such a way that
    it would pass beyond. If in the first way, then the thing will not be seen
    in itself but only its image will be seen as if it were the thing itself.
    That is the role of a memory species, not a visual one. If in the second
    way, then after the inspection of the species it will inspect the object in
    itself. In this way it will cognize the object in two ways, first through
    the species and second in itself. It will indeed be like when someone sees
    an intervening space and then beyond that sees the fixed object.
    """

    name: str
    """
    A thing that stands in for the object in the mind.

    When the exterior thing in-and-of-itself (per se) is not placed before the
    attention, there must be a memorative species placed before it in lieu of
    the object, which [the species] is not the origin of the cognitive act,
    except insofar as it serves as a term for or representative of the object.
    """

    id: Optional[int] = None

    created: datetime = field(default_factory=datetime.now)
    """
    Being is dynamic.

    The dynamic nature of being should be the primary focus of any
    comprehensive philosophical account of reality and our place within it.
    """

"""Provides functions that mutate domain objects."""

import random
from zero.domain import Thing, Baz


def add_some_one_to_the_thing(the_thing: Thing) -> None:
    """
    Add some ones to the name of a :class:`.Thing`.

    Parameters
    ----------
    the_thing : :class:`.Thing`

    """
    the_thing.name += "1" * random.randint(1, 10)


def increment_mukluk(a_thing: Thing, a_baz: Baz) -> None:
    """
    More mukluk.

    Parameters
    ----------
    a_thing : :class:`.Thing`
    a_baz : :class:`.Baz`

    """
    a_baz.mukluk += a_thing.name.count('1')
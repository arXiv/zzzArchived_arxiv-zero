"""Describes what a baz."""

from dataclasses import dataclass


@dataclass
class Baz:
    """Baz est ut mi semper mattis non eget tellus."""

    foo: str
    """Foo a tellus sit amet purus pharetra gravida vulputate ut purus."""

    mukluk: int
    """A soft boot, traditionally made of reindeer skin or sealskin."""

    @property
    def is_indeed(self) -> bool:
        """Determine whether the baz."""
        return self.mukluk > 5
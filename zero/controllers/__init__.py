"""
Contains arxiv-zero controllers.

We separate controllers from the Flask-style routes/blueprints to make them
easier to test. Controllers should not use Flask proxies directly; if something
in the request or the application context is needed, it should be parameterized
as part of the controller's signature.
"""

from .baz import get_baz
from .things import get_thing, create_a_thing, start_mutating_a_thing, \
    mutation_status, get_thing_description
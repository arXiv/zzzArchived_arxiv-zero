"""Provides routes for the external user interface."""

from flask import Blueprint, render_template, url_for, abort
from zero import status, authorization
from zero.controllers import baz, things

blueprint = Blueprint('ui', __name__, url_prefix='/zero/ui')


@blueprint.route('/baz/<int:baz_id>', methods=['GET'])
def read_baz(baz_id: int) -> tuple:
    """Provide some data about the baz."""
    data, status_code, headers = baz.get_baz(baz_id)
    if data is None:    # Render the generic 404 Not Found page.
        abort(status.HTTP_404_NOT_FOUND)
    if status_code != status.HTTP_200_OK:
        abort(status_code)
    response = render_template("zero/baz.html", **data)
    return response, status_code, headers


@blueprint.route('/thing/<int:thing_id>', methods=['GET'])
@authorization.scoped('read:thing')
def read_thing(thing_id: int) -> tuple:
    """Provide some data about the thing."""
    data, status_code, headers = things.get_thing(thing_id)
    if data is None:
        abort(status.HTTP_404_NOT_FOUND)
    if status_code != status.HTTP_200_OK:
        abort(status_code)
    response = render_template("zero/thing.html", **data)
    return response, status_code, headers

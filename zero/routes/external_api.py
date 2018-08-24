"""
Provides routes for the external API.

We also define some custom error handlers here. Since this is a JSON API, we
want our exception handlers to return JSON rather than the default template
rendering provided by ``arxiv.base``. See :func:`handle_exception`.
"""

from flask.json import jsonify
from flask import Blueprint, request, Response, make_response
from werkzeug.exceptions import NotFound, Forbidden, Unauthorized, \
    InternalServerError, HTTPException, BadRequest
from arxiv import status
from zero import authorization
from zero.controllers import baz, things

blueprint = Blueprint('external_api', __name__, url_prefix='/zero/api')


@blueprint.route('/status', methods=['GET'])
def ok() -> tuple:
    """Health check endpoint."""
    return jsonify({'status': 'nobody but us hamsters'}), status.HTTP_200_OK


@blueprint.route('/baz/<int:baz_id>', methods=['GET'])
def read_baz(baz_id: int) -> tuple:
    """Provide some data about the baz."""
    data, status_code, headers = baz.get_baz(baz_id)
    return jsonify(data), status_code, headers


@blueprint.route('/thing/<int:thing_id>', methods=['GET'])
@authorization.scoped('read:thing')
def read_thing(thing_id: int) -> tuple:
    """Provide some data about the thing."""
    data, status_code, headers = things.get_thing(thing_id)
    return jsonify(data), status_code, headers


@blueprint.route('/thing', methods=['POST'])
@authorization.scoped('write:thing')
def create_thing() -> tuple:
    """Create a new thing."""
    payload = request.get_json(force=True)    # Ignore Content-Type header.
    data, status_code, headers = things.create_a_thing(payload)
    return jsonify(data), status_code, headers


@blueprint.route('/thing/<int:thing_id>', methods=['POST'])
@authorization.scoped('write:thing')
def mutate_thing(thing_id: int) -> tuple:
    """Request that the thing be mutated."""
    data, status_code, headers = things.start_mutating_a_thing(thing_id)
    return jsonify(data), status_code, headers


@blueprint.route('/mutation/<string:task_id>', methods=['GET'])
@authorization.scoped('write:thing')
def mutation_status(task_id: str) -> tuple:
    """Get the status of the mutation task."""
    data, status_code, headers = things.mutation_status(task_id)
    return jsonify(data), status_code, headers


# Here's where we register exception handlers.

@blueprint.errorhandler(NotFound)
@blueprint.errorhandler(InternalServerError)
@blueprint.errorhandler(Forbidden)
@blueprint.errorhandler(Unauthorized)
@blueprint.errorhandler(BadRequest)
def handle_exception(error: HTTPException) -> Response:
    """
    JSON-ify the error response.

    This works just like the handlers in zero.routes.ui, but instead of
    rendering a template we are JSON-ifying the response. Note that we are
    registering the same error handler for several different exceptions, since
    we aren't doing anything that is specific to a particular exception.
    """
    content = jsonify({'reason': error.description})

    # Each Werkzeug HTTP exception has a class attribute called ``code``; we
    # can use that to set the status code on the response.
    response = make_response(content, error.code)
    return response

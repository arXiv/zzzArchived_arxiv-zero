"""
Provides routes for the external API.

We also define some custom error handlers here. Since this is a JSON API, we
want our exception handlers to return JSON rather than the default template
rendering provided by ``arxiv.base``. See :func:`handle_exception`.
"""

import io

from flask.json import jsonify
from flask import Blueprint, request, Response, make_response, send_file
from werkzeug.exceptions import NotFound, Forbidden, Unauthorized, \
    InternalServerError, HTTPException, BadRequest

from arxiv import status
from arxiv.users.domain import Scope
from arxiv.users.auth.decorators import scoped

from .. import controllers

# Normally these would be defined in the ``arxiv.users`` package, so that we
# can explicitly grant them when an authenticated session is created. These
# are defined here for demonstration purposes only.
READ_THING = Scope('thing', Scope.actions.READ)
WRITE_THING = Scope('thing', Scope.actions.UPDATE)

blueprint = Blueprint('external_api', __name__, url_prefix='/zero/api')


@blueprint.route('/status', methods=['GET'])
def ok() -> Response:
    """Health check endpoint."""
    response: Response = jsonify({'status': 'nobody but us hamsters'})
    return response


@blueprint.route('/baz/<int:baz_id>', methods=['GET'])
def read_baz(baz_id: int) -> Response:
    """Provide some data about the baz."""
    data, status_code, headers = controllers.get_baz(baz_id)
    response: Response = jsonify(data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


@blueprint.route('/thing/<int:thing_id>', methods=['GET'])
@scoped(READ_THING)
def read_thing(thing_id: int) -> Response:
    """Provide some data about the thing."""
    data, status_code, headers = controllers.get_thing(thing_id)
    if isinstance(data, io.BytesIO):
        mimetype = headers.get('Content-type', 'text/plain')
        response: Response = send_file(data, mimetype=mimetype)
    else:
        response = jsonify(data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


@blueprint.route('/thing', methods=['POST'])
@scoped(WRITE_THING)
def create_thing() -> Response:
    """Create a new thing."""
    payload = request.get_json(force=True)    # Ignore Content-Type header.
    data, status_code, headers = controllers.create_a_thing(payload)
    response: Response = jsonify(data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


@blueprint.route('/thing/<int:thing_id>', methods=['POST'])
@scoped(WRITE_THING)
def mutate_thing(thing_id: int) -> Response:
    """Request that the thing be mutated."""
    data, status_code, headers = controllers.start_mutating_a_thing(thing_id)
    response: Response = jsonify(data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


@blueprint.route('/mutation/<string:task_id>', methods=['GET'])
@scoped(WRITE_THING)
def mutation_status(task_id: str) -> Response:
    """Get the status of the mutation task."""
    data, status_code, headers = controllers.mutation_status(task_id)
    response: Response = jsonify(data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


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
    response: Response = make_response(content, error.code)
    return response

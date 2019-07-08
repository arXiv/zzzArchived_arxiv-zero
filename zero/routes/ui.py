"""
Provides routes for the external user interface.

The heart of this module is the ``blueprint`` object, an instance of
:class:`flask.Blueprint`. The blueprint pulls together a set of URL routing
rules that are attached to the Flask application in :mod:`.factory`.

Exception handling
------------------
We also attach exception handlers to the blueprint, so that we can render
responses that are tailored to this specific set of routes. Since this module
defines a blueprint for HTML user interfaces, our exception handlers here will
generate HTML responses. Note also that :mod:`arxiv.base.exceptions` provides
a set of default HTML error handlers, which may be sufficient for most
use-cases and will catch anything not handled on the blueprint.

Note that each handler renders a custom template (in
zero/templates/zero/). Each of those templates extends a template in
arxiv.base that provides the general layout and the funky
skull-and-crossbones image. See
http://github.com/arxiv/arxiv-base/tree/master/arxiv/base/templates/base

See :func:`handle_bad_request`.

"""

from flask import Blueprint, render_template, url_for, Response, make_response
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized, \
    Forbidden, InternalServerError
from arxiv import status

from arxiv.users.domain import Scope
from arxiv.users.auth.decorators import scoped

from .. import controllers

# Normally these would be defined in the ``arxiv.users`` package, so that we
# can explicitly grant them when an authenticated session is created. These
# are defined here for demonstration purposes only.
READ_THING = Scope('thing', Scope.actions.READ)
WRITE_THING = Scope('thing', Scope.actions.UPDATE)

blueprint = Blueprint('ui', __name__, url_prefix='/zero/ui')


@blueprint.route('/baz/<int:baz_id>', methods=['GET'])
def read_baz(baz_id: int) -> Response:
    """Provide some data about the baz."""
    data, status_code, headers = controllers.get_baz(baz_id)
    if not isinstance(data, dict):
        raise InternalServerError('Unexpected data')
    response: Response = render_template("zero/baz.html", **data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


@blueprint.route('/thing/<int:thing_id>', methods=['GET'])
@scoped(READ_THING)
def read_thing(thing_id: int) -> Response:
    """Provide some data about the thing."""
    data, status_code, headers = controllers.get_thing_description(thing_id)
    if not isinstance(data, dict):
        raise InternalServerError('Unexpected data')
    response: Response = render_template("zero/thing.html", **data)
    response.headers.extend(headers)
    response.status_code = status_code
    return response


# Here's where we register custom error handlers for this blueprint. These will
# catch the indicated Werkzeug exceptions that are raised within the context
# of this blueprint (i.e. while executing any of the routes above).


@blueprint.errorhandler(BadRequest)
def handle_bad_request(error: BadRequest) -> Response:
    """
    Render a custom error page for 400 Bad Request responses.

    The ``pagetitle`` context variable sets the ``title`` in the document
    head. The exception message is used to generate the message below the
    error code image.
    """
    rendered = render_template("zero/400_bad_request.html", error=error,
                               pagetitle="Nope! 400 Bad Request")
    response: Response = make_response(rendered)
    response.status_code = status.HTTP_400_BAD_REQUEST
    return response


@blueprint.errorhandler(Unauthorized)
def handle_unauthorized(error: Unauthorized) -> Response:
    """Render a custom error page for 401 Unauthorized responses."""
    rendered = render_template("zero/401_unauthorized.html", error=error,
                               pagetitle="Who are you?")
    response: Response = make_response(rendered)
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return response

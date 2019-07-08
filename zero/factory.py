"""Application factory for zero app."""

from flask import Flask

from arxiv.base import logging
from arxiv.util.serialize import ISO8601JSONEncoder
from arxiv.users import auth
from arxiv.base.middleware import wrap
from arxiv.base import Base

from .routes import external_api, ui
from .services import baz, things
from .celery import celery_app


# We defer configuration to app creation time, so that we have an opportunity 
# to use env-defined values.
def _configure_celery_app() -> None:
    from . import celeryconfig
    celery_app.config_from_object(celeryconfig)


def _create_base_app() -> Flask:
    app = Flask('zero')
    app.config.from_pyfile('config.py')
    app.json_encoder = ISO8601JSONEncoder

    baz.BazService.init_app(app)
    things.init_app(app)

    Base(app)    # Gives us access to the base UI templates and resources.
    auth.Auth(app)    # Sets up authn/z machinery.
    wrap(app, [auth.middleware.AuthMiddleware])
    return app


def create_web_app() -> Flask:
    """Initialize and configure the zero application."""
    app = _create_base_app()
    app.register_blueprint(ui.blueprint)
    return app


def create_api_app() -> Flask:
    app = _create_base_app()
    app.register_blueprint(external_api.blueprint)
    return app


def create_worker_app() -> Flask:
    """Initialize the zero worker application."""
    return _create_base_app()

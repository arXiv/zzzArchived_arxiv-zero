"""Application factory for zero app."""

import logging

from flask import Flask

from zero.routes import external_api, ui
from zero.services import baz, things
from zero.encode import ISO8601JSONEncoder
from baseui import BaseUI


def create_web_app() -> Flask:
    """Initialize and configure the zero application."""
    app = Flask('zero')
    app.config.from_pyfile('config.py')
    app.json_encoder = ISO8601JSONEncoder

    baz.init_app(app)
    things.init_app(app)

    BaseUI(app)    # Gives us access to the base UI templates and resources.
    app.register_blueprint(external_api.blueprint)
    app.register_blueprint(ui.blueprint)
    return app

"""Application factory for zero app."""

import logging

from flask import Flask

from zero.routes import external_api
from zero.services import baz, things
from zero.encode import ISO8601JSONEncoder


def create_web_app() -> Flask:
    """Initialize and configure the zero application."""
    app = Flask('zero')
    app.config.from_pyfile('config.py')
    app.json_encoder = ISO8601JSONEncoder
    baz.init_app(app)
    things.db.init_app(app)
    app.register_blueprint(external_api.blueprint)
    return app

"""Provides routes for the external API."""

from flask.json import jsonify
from flask import Blueprint, render_template, redirect, request, url_for
from zero import status
from zero.controllers import baz, things

blueprint = Blueprint('zero', __name__, url_prefix='/zero')


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
def read_thing(thing_id: int) -> tuple:
    """Provide some data about the thing."""
    data, status_code, headers = things.get_thing(thing_id)
    return jsonify(data), status_code, headers

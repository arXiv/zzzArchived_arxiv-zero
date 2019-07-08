"""This script runs the tests in :mod:`arxiv.base.app_tests`."""

import unittest

from arxiv.base.app_tests import *
from zero.factory import create_web_app

app = create_web_app()

if __name__ == '__main__':
    with app.app_context():
        unittest.main()
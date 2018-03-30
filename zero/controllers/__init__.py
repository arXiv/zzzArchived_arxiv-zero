"""
Contains arxiv-zero controller sketches.

We separate controllers from the Flask-style routes/blueprints to make them
easier to test. Controllers should not use Flask proxies directly; if something
in the request or the application context is needed, it should be parameterized
as part of the controller's signature.
"""

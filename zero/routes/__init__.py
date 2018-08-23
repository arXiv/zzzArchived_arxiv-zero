"""
Routes provide the glue between Flask and application :mod:`.controllers`.

Separate routes modules can be used to provide distinct interfaces, e.g. to
differentiate user-facing routes that return HTML from external APIs exposed
via the  arXiv API gateway. Each module should provide a
:class:`flask.Blueprint` that defines the routes exposed by that interface.

This is where request information is obtained from Flask proxy objects,
and where response data is serialized/rendered for return to the client.
"""

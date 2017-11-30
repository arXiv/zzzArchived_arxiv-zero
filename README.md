# arXiv Zero

This is a sample project for a microservice implemented in Flask, as part of
arXiv-NG. The goal of this project is to demonstrate the layout of a
microservice project in NG, desired internal architecture, testing and
documentation strategies, etc.

A developer working on a new microservice should be able to clone this
repository and build from there. This should lead to greater consistency
across microservice projects, and cut down on time spent on project setup.

## Running the development server

Flask provides a single-threaded dev server for your enjoyment.

The entrypoint for this dev server is [``app.py``](app.py) (in the root of the
project). Flask expects the path to this entrypoint in the environment variable
``FLASK_APP``. To run the dev server, try (from the project root):

```bash
$ FLASK_APP=app.py FLASK_DEBUG=1 flask run
```

``FLASK_DEBUG=1`` enables a slew of lovely development and debugging features.
For example, the dev server automatically restarts when you make changes to the
application code.

Note that neither the dev server or the ``app.py`` entrypoint are acceptable
for use in production.

A convenience script [``populate_test_database.py``](populate_test_database.py)
is provided to set up an on-disk SQLite database and some sample data. You can
use this as a starting point for more complex set-up operations (or not). Be
sure to run this with the ``FLASK_APP`` variable set, e.g.

```bash
$ FLASK_APP=app.py python populate_test_database.py
```

## Testing

Some example unit tests are provided in [``tests/``](tests/). They are written
using the built-in [unit-test](https://docs.python.org/3/library/unittest.html)
framework.

We use the [nose2](http://nose2.readthedocs.io/en/latest/) test runner, with
coverage. For example:

```bash
$ nose2 --with-coverage
..............
----------------------------------------------------------------------
Ran 14 tests in 0.109s

OK
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app.py                                  2      2     0%
populate_test_database.py              14     14     0%
tests/test_routes_external_api.py      40      4    90%
tests/test_routes_ui.py                24      0   100%
tests/test_service_foo.py              68      0   100%
tests/test_service_things.py           30      0   100%
wsgi.py                                 7      7     0%
zero/__init__.py                        0      0   100%
zero/authorization.py                  20      3    85%
zero/config.py                         12      0   100%
zero/context.py                        16      6    62%
zero/controllers/__init__.py            0      0   100%
zero/controllers/baz.py                13      4    69%
zero/controllers/things.py             13      4    69%
zero/encode.py                         12      5    58%
zero/factory.py                        16      0   100%
zero/logging.py                        16      3    81%
zero/routes/__init__.py                 0      0   100%
zero/routes/external_api.py            17      1    94%
zero/routes/ui.py                      23      4    83%
zero/services/__init__.py               1      0   100%
zero/services/baz.py                   54     10    81%
zero/services/things.py                20      0   100%
zero/status.py                         45      0   100%
-------------------------------------------------------
TOTAL                                 463     67    86%
```

## Code style

All new code should adhere as closely as possible to
[PEP008](https://www.python.org/dev/peps/pep-0008/).

Use the [Numpy style](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt)
for docstrings.

### Linting

Use [Pylint](https://www.pylint.org/) to check your code prior to raising a
pull request. The parameters below will be used when checking code  cleanliness
on commits, PRs, and tags, with a target score of >= 9/10.

If you're using Atom as your text editor, consider using the [linter-pylama](https://atom.io/packages/linter-pylama)
package for real-time feedback.

```bash
$ pylint --disable=W0622,W0611,F0401,R0914,W0221,W0222,W0142,F0010,W0703,R0911,C0103,R0913 -f parseable zero
No config file found, using default configuration
************* Module zero.context
zero/context.py:10: [W0212(protected-access), get_application_config] Access to a protected member _Environ of a client class
************* Module zero.encode
zero/encode.py:11: [E0202(method-hidden), ISO8601JSONEncoder.default] An attribute defined in json.encoder line 158 hides this method
************* Module zero.controllers.baz
zero/controllers/baz.py:1: [C0102(blacklisted-name), ] Black listed name "baz"
************* Module zero.services.baz
zero/services/baz.py:1: [C0102(blacklisted-name), ] Black listed name "baz"
************* Module zero.services.things
zero/services/things.py:11: [R0903(too-few-public-methods), Thing] Too few public methods (0/2)
zero/services/things.py:49: [E1101(no-member), get_a_thing] Instance of 'scoped_session' has no 'query' member

------------------------------------------------------------------
Your code has been rated at 9.49/10 (previous run: 9.41/10, +0.07)
```

## Type hints and static checking
Use [type hint annotations](https://docs.python.org/3/library/typing.html)
wherever practicable. Use [mypy](http://mypy-lang.org/) to check your code.

Try running mypy with (from project root):

```bash
$ mypy -p zero --ignore-missing-imports
```

mypy chokes on dynamic base classes and proxy objects (which you're likely
to encounter using Flask); it's perfectly fine to disable checking on those
offending lines using "``# type: ignore``". For example:

```python
>>> g.baz = get_session(app) # type: ignore
```


See [this issue](https://github.com/python/mypy/issues/500>) for more
information.

## Documentation

Documentation is built with [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html).
The documentation source files (in [reST markdown](http://www.sphinx-doc.org/en/stable/rest.html))
are in ``docs/source``. Everything in that directory **is** under version
control. The rendered documentation is located in ``docs/build``; those files
are **not** under version control (per ``.gitignore``).

To build the full documentation for this project:

```bash
$ cd <project_root>/docs
$ make html
```

Point your browser to: ``file:///path/to/arxiv-zero/docs/build/html/index.html``.

There are other build targets available. Run ``make`` without any arguments
for more info.

### Architecture

Architectural documentation is located at
[``docs/source/architecture.rst``](docs/source/architecture.rst). This can be
exploded into multiple files, if necessary.

This architecture documentation is based on the [arc42](http://arc42.org/)
documentation model, and also draws heavily on the [C4 software architecture
model](https://www.structurizr.com/help/c4>). The C4 model describes an
architecture at four hierarchical levels, from the business context of the
system to the internal architecture of small parts of the system.

In document for arXiv NG services, we have departed slightly from the original
language of C4 in order to avoid collision with names in adjacent domains.
Specifically, we describe the system at three levels:

1. **Context**: This includes both the business and technical contexts in the
   arc42 model. It describes the interactions between a service and
   other services and systems.
2. **Building block**: This is similar to the "container" concept in the C4
   model. A building block is a part of the system that is developed, tested,
   and deployed quasi-independently. This might be a single application, or
   a data store.
3. **Component**: A component is an internal part of a building block. In the
   case of a Flask application, this might be a module or submodule that has
   specific responsibilities, behaviors, and interactions.


### Code API documentation

Documentation for the (code) API is generated automatically with
[sphinx-apidoc](http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html),
and lives in ``docs/source/api``.

sphinx-apidoc generates references to modules in the code, which are followed
at build time to retrieve docstrings and other details. This means that you
won't need to run sphinx-apidoc unless the structure of the project changes
(e.g. you add/rename a module).

To rebuild the API docs, run (from the project root):

``sphinx-apidoc -M -f -o docs/source/api/ zero``


## TODO

- Add docker image push step to .travis.yml (needs authentication).
- Incorporate JSON schema into documentation.
- Add an example e2e test.
- Add an example controller test.

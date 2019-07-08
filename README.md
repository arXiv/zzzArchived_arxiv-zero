[![Build Status](https://img.shields.io/travis/arxiv/arxiv-zero/master.svg)](https://travis-ci.org/arxiv/arxiv-zero) [![Coverage Status](https://img.shields.io/coveralls/github/arXiv/arxiv-zero/master.svg)](https://coveralls.io/github/arxiv/arxiv-zero?branch=master)

# arXiv Zero

This is a sample project for a microservice implemented in Flask, as part of
arXiv-NG. The goal of this project is to demonstrate the layout of a
microservice project in NG, desired internal architecture, testing and
documentation strategies, etc.

For a more complete description of the patterns demonstrated in this sample
app, see [Services in arXiv
NG](https://arxiv.github.io/arxiv-arxitecture/crosscutting/services.html).

A developer working on a new microservice should be able to clone this
repository and build from there. This should lead to greater consistency
across microservice projects, and cut down on time spent on project setup.

Before working with this repository, please be sure to review the [arXiv
Contributor
Guidelines](https://github.com/arXiv/.github/blob/master/CONTRIBUTING.md).

## Quick start

### Local Deployment

Sometimes Docker adds more overhead than you want, especially when making quick
changes. We assume your developer machine already has a version of Python 3.6
with `pip`.

1.  `pip install pipenv && pipenv install --dev`
2.  `FLASK_APP=app.py pipenv run python populate_test_database.py`
3.  `JWT_SECRET=foosecret FLASK_APP=app.py FLASK_DEBUG=1 pipenv run flask run`

#### Notes on the development server

Flask provides a single-threaded dev server for your enjoyment.

The entrypoint for this dev server is [``app.py``](app.py) (in the root of the
project). Flask expects the path to this entrypoint in the environment variable
``FLASK_APP``. To run the dev server, try (from the project root):

```bash
$ FLASK_APP=app.py FLASK_DEBUG=1 pipenv run flask run
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
$ FLASK_APP=app.py pipenv run python populate_test_database.py
```


## Documentation

Documentation is built with
[Sphinx](http://www.sphinx-doc.org/en/stable/rest.html). The documentation
source files (in [reST
markdown](http://www.sphinx-doc.org/en/stable/rest.html)) are in
``docs/source``. Everything in that directory **is** under version control. The
rendered documentation is located in ``docs/build``; those files are **not**
under version control (per ``.gitignore``).

To build the full documentation for this project:

```bash
cd <project_root>/docs
make html SPHINXBUILD=$(pipenv --venv)/bin/sphinx-build
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

```bash
$ sphinx-apidoc -M -f -o docs/source/api/ zero
```


## TODO

- Add docker image push step to .travis.yml (needs authentication).
- Incorporate JSON schema into documentation.

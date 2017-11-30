# arXiv Zero

This is a sample project for a microservice implemented in Flask, as part of
arXiv-NG. The goal of this project is to demonstrate the layout of a
microservice project in NG, desired internal architecture, testing and
documentation strategies, etc.

A developer working on a new microservice should be able to clone this
repository and build from there. This should lead to greater consistency
across microservice projects, and cut down on time spent on project setup.


## Documentation

Documentation is built with [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html).
The documentation source files (in [reST markdown]
(http://www.sphinx-doc.org/en/stable/rest.html)) are in ``docs/source``.
Everything in that directory **is** under version control. The rendered
documentation is located in ``docs/build``; those files are **not** under
version control (per ``.gitignore``).

To build the full documentation for this project:

```bash
cd <project_root>/docs
make html
```

Point your browser to: ``file:///path/to/arxiv-zero/docs/build/html/index.html``.

There are other build targets available. Run ``make`` without any arguments
for more info.

### Architecture

Architectural documentation is located in ``docs/source/architecture.rst``.
This can be exploded into multiple files, if necessary.

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

"""An authorized client can create and mutate a :class:`.Thing`."""

import threading
import json
import tempfile
import shutil
import os
import time
from unittest import TestCase, mock
from urllib import parse
from http import HTTPStatus

from arxiv.users.helpers import generate_token
from zero.routes.external_api import READ_THING, WRITE_THING


class TestCreateAndMutate(TestCase):
    """
    Test creation and mutation of :class:`.Thing` via external API.

    Uses on-disk SQLite DBs and an in-memory quque. Integration with *SQL
    and Redis should be tested separately.
    """

    def setUp(self) -> None:
        """Initialize in-memory queue, on-disk database, and test client."""
        os.environ['JWT_SECRET'] = 'foosecret'
        from zero.factory import create_web_app, celery_app, create_api_app

        # Initialize the web application with an on-disk test database.
        self.app = create_api_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

        self.client = self.app.test_client()

        # Use the ``things`` service as a convenient hook into the DB.
        from zero.services import things
        self.things = things
        self.things.init_app(self.app)
        with self.app.app_context():
            self.things.create_all()

        # Use an in-memory queue, and an on-disk SQLite DB for results.
        celery_app.conf.broker_url = 'memory://localhost/'
        self.temppath = tempfile.mkdtemp()
        celery_app.conf.result_backend = f'file://{self.temppath}'
        celery_app.conf.worker_prefetch_multiplier = 1
        celery_app.conf.task_acks_late = True
        celery_app.conf.task_always_eager = False

        # Start a worker in a separate thread.
        def run_worker() -> None:
            """Wrap :func:`Celery.worker_main` for multithreading."""
            with self.app.app_context():
                celery_app.worker_main(['--loglevel=DEBUG', '-E'])

        t = threading.Thread(target=run_worker)
        t.daemon = True
        t.start()

    def tearDown(self) -> None:
        """Clear the database and tear down all tables, clean up filesystem."""
        with self.app.app_context():
            self.things.db.session.remove() # type: ignore
            self.things.db.drop_all() # type: ignore
        shutil.rmtree(self.temppath)

    def test_create_a_thing_and_mutate_it(self) -> None:
        """Create and mutate a thing via the API."""
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[READ_THING, WRITE_THING])
        thing_data = {'name': 'The Thing'}

        # Create the thing:
        #
        #  Client                App              Database
        #    |                    |                  |
        #    | -- POST /thing --> |                  |
        #    |                    | -- Write row --> |
        #    |                    | <-- Row data --- |
        #    | <-- 201 w/ data -- |
        #   Location: /thing/<id>
        response = self.client.post('/zero/api/thing',
                                    data=json.dumps(thing_data),
                                    headers={'Authorization': token},
                                    content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.CREATED, "Created")

        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], thing_data['name'])
        self.assertIn('created', response_data)
        self.assertIn('id', response_data)
        self.assertIn('url', response_data)

        # Get the thing:
        #
        #  Client                  App                 Database
        #    |                      |                     |
        #    | - GET /thing/<id> -> |                     |
        #    |                      | -- Select by ID --> |
        #    |                      | <---- Row data ---- |
        #    | <--- 200 w/ data --  |
        get_response = self.client.get(response_data['url'],
                                       headers={'Authorization': token})
        self.assertEqual(get_response.data, b'The Thing')

        # Mutate the thing:
        #
        #  Client                     App              Queue
        #    | -- POST /thing/<id> --> |                  |
        #    |                         |                  |
        #    |                         | --- New task --> |
        #    |                         | <--- Task ID --- |
        #    | <--- 202 w/task ID ---- |
        #   Location: /mutation/<task id>
        mutate_response = self.client.post(response_data['url'],
                                           data=json.dumps({}),
                                           headers={'Authorization': token},
                                           content_type='application/json')
        self.assertEqual(mutate_response.status_code, HTTPStatus.ACCEPTED,
                         "Accepted")

        # Get mutation task status (not yet complete):
        #
        #  Client                            App              Results
        #    | -- GET /mutation/<task id> --> |                  |
        #    |                                | -- Get task ---> |
        #    |                                | <- Task status - |
        #    | <----- 200 w/task status ----- |
        status_path = parse.urlparse(mutate_response.headers['Location']).path
        status_response = self.client.get(status_path,
                                          headers={'Authorization': token})
        self.assertEqual(status_response.status_code, HTTPStatus.OK,
                         "Status resource found")

        # Meanwhile, worker process gets task and executes:
        #
        #  Worker            Queue      Database    Results
        #    | -- POP task --> |           |          |
        #    | <- Task sig. -- |           |          |
        #    |                             |          |
        #    | ----- Get thing by ID --- > |          |
        #    | <---- Return thing data --- |          |
        #    .. .. .. .. .. work work work .. .. .. ..
        #    | --- Update thing data --- > |          |
        #    | <---- Return thing data --- |          |
        #    |                                        |
        #    | ----------- Update result -----------> |
        time.sleep(6)    # Wait for task to complete.

        # Get mutation task status (complete):
        #
        #  Client                            App              Results
        #    | -- GET /mutation/<task id> --> |                  |
        #    |                                | -- Get task ---> |
        #    |                                | <- Task status - |
        #    | <----- 303 w/task status ----- |
        #   Location: /thing/<id>
        status_response = self.client.get(status_path,
                                          headers={'Authorization': token})
        self.assertEqual(status_response.status_code, HTTPStatus.SEE_OTHER,
                         "See other")
        status_response_data = json.loads(status_response.data)

        self.assertIn("result", status_response_data)
        self.assertIn("status", status_response_data)
        self.assertIn("location", status_response.headers)
        N_ones = status_response_data['result']['result'] - 9

        # Get the thing one last time:
        #
        #  Client                  App                 Database
        #    |                      |                     |
        #    | - GET /thing/<id> -> |                     |
        #    |                      | -- Select by ID --> |
        #    |                      | <---- Row data ---- |
        #    | <--- 200 w/ data --  |
        final_response = self.client.get(
            parse.urlparse(status_response.headers['Location']).path,
            headers={'Authorization': token}
        )
        self.assertEqual(final_response.status_code, HTTPStatus.OK, "OK")
        self.assertEqual(final_response.data, b'The Thing' + b'1' * N_ones)
        # final_response_data = json.loads()
        # self.assertIn('id', final_response_data)
        # self.assertIn('name', final_response_data)
        # self.assertIn('created', final_response_data)
        # self.assertEqual(N_chars, len(final_response_data['name']))

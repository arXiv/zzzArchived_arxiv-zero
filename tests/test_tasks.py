"""Tests for :mod:`zero.tasks`."""

from unittest import TestCase, mock
from datetime import datetime
from zero.domain import Thing
from zero import tasks


class TestMutateAThing(TestCase):
    """:func:`mutate_a_thing` mutates a Thing and updates the database."""

    @mock.patch('zero.tasks.mutate')
    @mock.patch('zero.tasks.things')
    def test_mutate(self, mock_things, mock_mutate):
        """A :class:`.Thing` is loaded, mutated, and stored."""
        thing_id = 24
        the_thing = Thing(id=thing_id, name='a thing', created=datetime.now())
        mock_things.get_a_thing.return_value = the_thing

        tasks.mutate_a_thing(thing_id, with_sleep=0.1)
        self.assertEqual(mock_things.get_a_thing.call_count, 1)
        self.assertEqual(mock_mutate.add_some_one_to_the_thing.call_count, 1)
        self.assertEqual(mock_things.update_a_thing.call_count, 1)

    @mock.patch('zero.tasks.mutate')
    @mock.patch('zero.tasks.things')
    def test_service_raises_ioerror(self, mock_things, mock_mutate):
        """An IOError raised by the service is allowed to propagate."""
        mock_things.get_a_thing.side_effect = IOError
        with self.assertRaises(IOError):
            tasks.mutate_a_thing(24)


class TestCheckTaskStatus(TestCase):
    """:func:`.check_mutation_status` checks the status of a mutation task."""

    def test_task_id_is_not_a_string(self):
        """A ValueError is raised when ``task_id`` is not a string."""
        with self.assertRaises(ValueError):
            tasks.check_mutation_status(1)

    @mock.patch('zero.tasks.AsyncResult')
    def test_task_result_is_returned_when_successful(self, mock_AsyncResult):
        """When task succeeds task result is returned."""
        task_id = 'a440s0x0kf0k04s'
        expected_result = 'The Result'
        mock_result = mock.MagicMock(status='SUCCESS', result=expected_result)
        mock_AsyncResult.return_value = mock_result

        status, result = tasks.check_mutation_status(task_id)

        self.assertEqual(result, expected_result)
        self.assertEqual(mock_AsyncResult.call_args[0][0], task_id)
        self.assertEqual(status, 'SUCCESS')

    @mock.patch('zero.tasks.AsyncResult')
    def test_task_result_is_returned_when_failed(self, mock_AsyncResult):
        """When task fails task result is returned."""
        task_id = 'a440s0x0kf0k04s'
        expected_result = 'The Result'
        mock_result = mock.MagicMock(status='FAILED', result=expected_result)
        mock_AsyncResult.return_value = mock_result

        status, result = tasks.check_mutation_status(task_id)

        self.assertEqual(result, expected_result)
        self.assertEqual(mock_AsyncResult.call_args[0][0], task_id)
        self.assertEqual(status, 'FAILED')

    @mock.patch('zero.tasks.AsyncResult')
    def test_task_result_is_none_when_pending(self, mock_AsyncResult):
        """When task is pending task result is None."""
        task_id = 'a440s0x0kf0k04s'
        eventual_result = 'The Result'
        mock_result = mock.MagicMock(status='PENDING', result=eventual_result)
        mock_AsyncResult.return_value = mock_result

        status, result = tasks.check_mutation_status(task_id)

        self.assertEqual(result, None)
        self.assertEqual(mock_AsyncResult.call_args[0][0], task_id)
        self.assertEqual(status, 'PENDING')

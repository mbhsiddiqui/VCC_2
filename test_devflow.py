"""Focused tests of the initial task tracker."""

from pathlib import Path
import tempfile
import unittest

from storage import load_tasks, save_tasks
from task_manager import add_task, complete_task, list_tasks


class BaselineTests(unittest.TestCase):
    def test_add_and_list_task(self):
        tasks = []
        created = add_task(tasks, "Review a change")
        self.assertEqual(created["title"], "Review a change")
        self.assertFalse(created["completed"])
        self.assertEqual(list_tasks(tasks), [created])

    def test_complete_task(self):
        tasks = []
        created = add_task(tasks, "Run tests")
        complete_task(tasks, created["id"])
        self.assertTrue(tasks[0]["completed"])

    def test_unknown_task_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            complete_task([], "missing")

    def test_missing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_tasks(Path(directory) / "tasks.json"), [])

    def test_storage_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            tasks = []
            add_task(tasks, "Ship a small improvement")
            save_tasks(path, tasks)
            self.assertEqual(load_tasks(path), tasks)


if __name__ == "__main__":
    unittest.main()

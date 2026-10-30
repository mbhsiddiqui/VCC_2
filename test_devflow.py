"""Focused tests of the initial task tracker."""

from pathlib import Path
from copy import deepcopy
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import UUID

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


class CreationTests(unittest.TestCase):
    def test_description_and_trimmed_title(self):
        task = add_task([], "  Review a change  ", "Check edge cases")
        self.assertEqual(task["title"], "Review a change")
        self.assertEqual(task["description"], "Check edge cases")
        self.assertEqual(str(UUID(task["id"])), task["id"])

    def test_description_defaults_to_empty(self):
        self.assertEqual(add_task([], "Run tests")["description"], "")

    def test_invalid_titles_do_not_mutate_tasks(self):
        for value in ("", "   ", "\t\n", None, 42):
            with self.subTest(value=value):
                tasks = []
                with self.assertRaisesRegex(ValueError, "title"):
                    add_task(tasks, value)
                self.assertEqual(tasks, [])

    def test_invalid_description_does_not_mutate_tasks(self):
        tasks = []
        with self.assertRaisesRegex(ValueError, "description"):
            add_task(tasks, "Run tests", None)
        self.assertEqual(tasks, [])

    def test_unique_ids_with_existing_tasks(self):
        tasks = [{"id": "1", "title": "Legacy task", "description": "", "completed": False}]
        first = add_task(tasks, "First new task")
        second = add_task(tasks, "Second new task")
        self.assertEqual(len({task["id"] for task in tasks}), 3)
        self.assertNotEqual(first["id"], second["id"])

    def test_uuid_collision_is_retried(self):
        existing = "00000000-0000-4000-8000-000000000001"
        replacement = "00000000-0000-4000-8000-000000000002"
        tasks = [{"id": existing}]
        with patch("task_manager.uuid4", side_effect=[UUID(existing), UUID(replacement)]):
            created = add_task(tasks, "New task")
        self.assertEqual(created["id"], replacement)
        self.assertEqual(len({task["id"] for task in tasks}), 2)

    def test_cli_creation_and_rejected_input_preserve_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            prefix = [sys.executable, str(Path(__file__).with_name("devflow.py")),
                      "--data-file", str(path)]
            result = subprocess.run(prefix + ["add", "  Review  ", "--description", "Details"],
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            records = json.loads(path.read_text())
            self.assertEqual(records[0]["title"], "Review")
            self.assertEqual(records[0]["description"], "Details")
            self.assertIn(records[0]["id"], result.stdout)
            before = path.read_bytes()
            invalid = subprocess.run(prefix + ["add", "   "],
                                     text=True, capture_output=True, timeout=10)
            self.assertEqual(invalid.returncode, 2)
            self.assertIn("nonempty", invalid.stderr)
            self.assertEqual(path.read_bytes(), before)


class FilteringTests(unittest.TestCase):
    def setUp(self):
        self.tasks = []
        self.first = add_task(self.tasks, "First pending")
        self.second = add_task(self.tasks, "Completed item")
        self.third = add_task(self.tasks, "Last pending")
        complete_task(self.tasks, self.second["id"])

    def test_all_is_the_default_and_returns_a_separate_list(self):
        result = list_tasks(self.tasks)
        self.assertEqual(result, self.tasks)
        self.assertIsNot(result, self.tasks)
        result.pop()
        self.assertEqual(len(self.tasks), 3)

    def test_pending_and_completed_keep_original_order(self):
        before = deepcopy(self.tasks)
        self.assertEqual(list_tasks(self.tasks, "pending"), [self.first, self.third])
        self.assertEqual(list_tasks(self.tasks, "completed"), [self.second])
        self.assertEqual(self.tasks, before)

    def test_empty_selections(self):
        for status in ("all", "pending", "completed"):
            with self.subTest(status=status):
                self.assertEqual(list_tasks([], status), [])
        self.assertEqual(list_tasks([self.second], "pending"), [])
        self.assertEqual(list_tasks([self.first], "completed"), [])

    def test_invalid_status_is_rejected_without_mutation(self):
        before = deepcopy(self.tasks)
        for status in ("done", "", None, 1):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError, "status"):
                    list_tasks(self.tasks, status)
        self.assertEqual(self.tasks, before)

    def test_cli_filters_persisted_mixed_states_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            save_tasks(path, self.tasks)
            before = path.read_bytes()
            prefix = [sys.executable, str(Path(__file__).with_name("devflow.py")),
                      "--data-file", str(path), "list"]
            for status, included, excluded in (
                ("all", ["First pending", "Completed item", "Last pending"], []),
                ("pending", ["First pending", "Last pending"], ["Completed item"]),
                ("completed", ["Completed item"], ["First pending", "Last pending"]),
            ):
                with self.subTest(status=status):
                    result = subprocess.run(prefix + ["--status", status],
                                            text=True, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for title in included:
                        self.assertIn(title, result.stdout)
                    for title in excluded:
                        self.assertNotIn(title, result.stdout)
                    self.assertEqual(path.read_bytes(), before)
            invalid = subprocess.run(prefix + ["--status", "done"],
                                     text=True, capture_output=True, timeout=10)
            self.assertEqual(invalid.returncode, 2)
            self.assertIn("invalid choice", invalid.stderr)
            self.assertEqual(path.read_bytes(), before)

    def test_cli_empty_filter_has_clear_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            save_tasks(path, [self.first])
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("devflow.py")),
                 "--data-file", str(path), "list", "--status", "completed"],
                text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "No tasks found.")


if __name__ == "__main__":
    unittest.main()

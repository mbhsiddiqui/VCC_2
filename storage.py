"""Validated JSON persistence with atomic replacement for single-process use."""

import json
import os
from pathlib import Path
import tempfile


class StorageError(Exception):
    """The task database could not be safely read or written."""


def validate_tasks(tasks):
    """Check stored fields without discarding extra fields or legacy string IDs."""
    if not isinstance(tasks, list):
        raise StorageError("Task database must contain a JSON list.")
    seen = set()
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise StorageError(f"Task {index} must be a JSON object.")
        for field in ("id", "title", "description"):
            if not isinstance(task.get(field), str):
                raise StorageError(f"Task {index} must have a string {field}.")
        if not task["id"].strip() or not task["title"].strip():
            raise StorageError(f"Task {index} must have a nonempty ID and title.")
        if type(task.get("completed")) is not bool:
            raise StorageError(f"Task {index} must have a boolean completed flag.")
        if task["id"] in seen:
            raise StorageError("Task database contains duplicate IDs.")
        seen.add(task["id"])


def load_tasks(path):
    """Read validated tasks; a missing file is empty and is never created."""
    try:
        with Path(path).open(encoding="utf-8") as handle:
            tasks = json.load(handle)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise StorageError(
            "Task database contains malformed JSON. Repair it or choose another "
            "--data-file; the database was not changed."
        ) from error
    except UnicodeError as error:
        raise StorageError("Task database must use valid UTF-8 text.") from error
    except OSError as error:
        raise StorageError("Cannot read task database. Check the path and permissions.") from error
    validate_tasks(tasks)
    return tasks


def save_tasks(path, tasks):
    """Replace the database only after a complete, flushed temporary write."""
    validate_tasks(tasks)
    temporary_path = None
    try:
        # Serialize first so invalid extra values cannot affect existing data.
        content = json.dumps(tasks, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        destination = Path(path)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=".devflow-", suffix=".tmp", delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    except (OSError, UnicodeError, TypeError, ValueError) as error:
        raise StorageError(
            "Cannot save task database. Check the parent directory and permissions; "
            "existing data was not replaced."
        ) from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                # Cleanup must not replace the original write error.
                pass

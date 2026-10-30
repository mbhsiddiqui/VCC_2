"""Basic JSON persistence for the initial DevFlow implementation."""

import json
from pathlib import Path


def load_tasks(path):
    """Read stored tasks; a missing file represents an empty collection."""
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return []


def save_tasks(path, tasks):
    """Write the current tasks to a JSON file."""
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(tasks, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

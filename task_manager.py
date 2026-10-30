"""In-memory task operations for the initial DevFlow implementation."""


def add_task(tasks, title):
    """Append a title-only task and return its record."""
    task = {
        "id": str(len(tasks) + 1),
        "title": title,
        "description": "",
        "completed": False,
    }
    tasks.append(task)
    return task


def list_tasks(tasks):
    """Return tasks in their original order."""
    return list(tasks)


def complete_task(tasks, task_id):
    """Complete a matching task; reject an unknown identifier."""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return task
    raise ValueError(f"Task {task_id} was not found.")

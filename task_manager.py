"""In-memory task operations for DevFlow."""

from uuid import uuid4


def add_task(tasks, title, description=""):
    """Validate and append a task with an ID distinct from existing tasks."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title must be a nonempty string.")
    if not isinstance(description, str):
        raise ValueError("Task description must be a string.")
    existing_ids = {task["id"] for task in tasks}
    task_id = str(uuid4())
    while task_id in existing_ids:
        task_id = str(uuid4())
    task = {
        "id": task_id,
        "title": title.strip(),
        "description": description,
        "completed": False,
    }
    tasks.append(task)
    return task


def list_tasks(tasks, status="all"):
    """Return matching tasks in original order without changing the collection."""
    if status not in ("all", "pending", "completed"):
        raise ValueError("Task status must be all, pending, or completed.")
    if status == "all":
        return list(tasks)
    completed = status == "completed"
    return [task for task in tasks if task["completed"] == completed]


def complete_task(tasks, task_id):
    """Complete a matching task; reject an unknown identifier."""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return task
    raise ValueError(f"Task {task_id} was not found.")

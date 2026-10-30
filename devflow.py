"""DevFlow command-line entry point."""

import argparse
import sys

from storage import load_tasks, save_tasks
from task_manager import add_task, complete_task, list_tasks


def build_parser():
    parser = argparse.ArgumentParser(description="Organize development tasks.")
    parser.add_argument("--data-file", default="tasks.json", help="JSON database path")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Create a task")
    add.add_argument("title")
    commands.add_parser("list", help="List all tasks")
    complete = commands.add_parser("complete", help="Complete a task")
    complete.add_argument("task_id")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    tasks = load_tasks(args.data_file)
    try:
        if args.command == "add":
            task = add_task(tasks, args.title)
            save_tasks(args.data_file, tasks)
            print(f"Created task {task['id']}: {task['title']}")
        elif args.command == "complete":
            task = complete_task(tasks, args.task_id)
            save_tasks(args.data_file, tasks)
            print(f"Completed task {task['id']}: {task['title']}")
        else:
            matches = list_tasks(tasks)
            if not matches:
                print("No tasks found.")
            for task in matches:
                status = "completed" if task["completed"] else "pending"
                print(f"{task['id']} [{status}] {task['title']}")
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# DevFlow CLI: Developer Productivity Toolkit

A Python task tracker built for Assignment #2: Version Control and Collaboration.

## Run DevFlow

Use Python 3; no external packages are required. Run commands from this repository:

```sh
python3 devflow.py --data-file tasks.json add "Review a change" --description "Check validation and tests"
python3 devflow.py --data-file tasks.json list
python3 devflow.py --data-file tasks.json complete TASK_ID
python3 devflow.py --data-file tasks.json list --status pending
python3 devflow.py --data-file tasks.json list --status completed
python3 -m unittest -v
```

The default database is `tasks.json` in the current directory. Missing files start an empty task list. Each command reads the JSON database, and changes are written back for later invocations. Keep local data untracked.

Creation accepts a nonempty title and an optional description. Titles are trimmed; empty or whitespace-only titles are rejected without changing stored tasks. Each new task receives a UUID checked against existing IDs. Copy the full ID printed by `add` or `list` into the `complete TASK_ID` command. Existing numeric IDs remain usable. Listing shows each task and any description.

Listing defaults to all tasks. Use `list --status all`, `list --status pending`, or `list --status completed` to select a status. Results retain creation order; an empty selection prints `No tasks found.` Invalid status values are rejected.

Safer persistence and expanded tests will arrive through separate issue-linked PRs. Storage currently uses basic JSON reads and direct writes; malformed JSON and operating-system failures are not yet handled gracefully. Do not use this introductory baseline for important data or concurrent writes.

`devflow.py` handles arguments and output, `task_manager.py` holds task operations, `storage.py` handles JSON, and `test_devflow.py` tests core operations and task creation. See CONTRIBUTING.md for the review workflow.

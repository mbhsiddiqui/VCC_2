# DevFlow CLI: Developer Productivity Toolkit

A Python task tracker built for Assignment #2: Version Control and Collaboration.

## Run the baseline

Use Python 3; no external packages are required. Run commands from this repository:

```sh
python3 devflow.py --data-file tasks.json add "Review a change"
python3 devflow.py --data-file tasks.json list
python3 devflow.py --data-file tasks.json complete 1
python3 -m unittest -v
```

The default database is `tasks.json` in the current directory. Missing files start an empty task list. Each command reads the JSON database, and changes are written back for later invocations. Keep local data untracked.

This initial implementation supports title-only creation, all-task listing, and completion. Input validation, descriptions, status filtering, safer persistence, and expanded tests will arrive through separate issue-linked PRs. Storage currently uses basic JSON reads and direct writes; malformed JSON and operating-system failures are not yet handled gracefully. Do not use this introductory baseline for important data or concurrent writes.

`devflow.py` handles arguments and output, `task_manager.py` holds task operations, `storage.py` handles JSON, and `test_devflow.py` tests the baseline. See CONTRIBUTING.md for the review workflow.

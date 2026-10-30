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

## Persistence and errors

JSON records are validated on read and write. Missing files represent an empty list; listing does not create or rewrite a database. A save writes a temporary file in the same directory, flushes and synchronizes it, then atomically replaces the database. Existing task fields, including extra metadata and legacy string IDs, are preserved. The parent directory must already exist.

Malformed JSON, invalid task records, invalid UTF-8, and filesystem errors produce concise diagnostics on stderr and exit code 1. Task-input errors return 2; successful commands return 0. Rejected input and unreadable databases are never silently replaced with empty data. Back up important task data. This tool supports one writer at a time: atomic replacement prevents partial writes, but there is no locking to protect concurrent read-modify-write operations.

[Issue #5](https://github.com/mbhsiddiqui/VCC_2/issues/5) records the genuine malformed-JSON crash in the baseline. The crash is corrected with controlled diagnostics and preservation tests here; the issue remains open for the assignment's required bug documentation, pending instructor-directed closure.

`devflow.py` handles arguments and output, `task_manager.py` holds task operations, `storage.py` handles JSON, and `test_devflow.py` contains unit tests and real-process CLI workflow tests. See CONTRIBUTING.md for the review workflow.


## Verify changes

Run `python3 -m unittest -v` from this repository. The suite covers creation, filtering, completion, cross-process persistence, Unicode, invalid input, corrupted databases, and safe-write failure handling. Tests use temporary directories and do not touch your normal task database. Permission failures are simulated where needed so the suite does not depend on the account running it.

Run `python3 -m py_compile devflow.py task_manager.py storage.py test_devflow.py` for syntax checks and `git diff --check` before committing. Keep generated `__pycache__/` directories excluded locally. Historical baseline defect reproduction is separate from the final passing regression suite; current malformed JSON returns a controlled error without modifying data.

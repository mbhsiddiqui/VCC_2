# Contributing

Use Python 3 and the standard library. Run these checks from the repository before proposing a change:

```sh
python3 -m unittest -v
python3 -m py_compile devflow.py task_manager.py storage.py test_devflow.py
git diff --check
```

Verify that unittest reports a nonzero test count. The suite isolates data in temporary directories and tests both task APIs and separate CLI processes. Test CLI commands with an explicit temporary `--data-file` so personal tasks are unaffected.

## Workflow

1. Describe the problem in an issue with acceptance criteria. For bugs, include the revision, environment, reproduction steps, expected behavior, and actual behavior.
2. Synchronize `dev` and create the relevant branch:
   - `feature/1-task-creation`
   - `feature/2-task-filtering`
   - `feature/3-persistent-storage`
   - `feature/4-test-coverage`
3. Implement only that issue, add focused tests, and make a meaningful commit.
4. Open a pull request targeting `dev`. Link the issue and describe the implementation, tests, and limitations.
5. Inspect the actual diff for correctness, validation, error handling, maintainability, and edge cases. Record substantive review findings and any resolutions in PR comments.
6. Merge after validation. Verify the merge and issue state on GitHub. Closing keywords targeting `dev` may not automatically close an issue while `main` is the default branch; verify and close resolved enhancement issues explicitly when necessary.
7. After all four enhancements, run the full suite and review an integration PR from `dev` to `main`. Keep the remote `dev` branch.

GitHub prevents authors from formally approving their own PRs. Document author self-review honestly; request a separate legitimate reviewer when available. Do not describe self-review as independent approval.

Keep generated Python caches, local task databases, and temporary data untracked through `.git/info/exclude`. This assignment tracks only README.md and the five specified project files. Keep the assignment report and evidence outside this repository. Never commit credentials or private project source.

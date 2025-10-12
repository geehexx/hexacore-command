---
description: Git commit workflow
auto_execution_mode: 3
---

# Git Commit Workflow

1. Run `functions.*_git_status` with the repo path to capture the baseline working tree state before alterations.
2. Perform the required edits, validations, and automated tests.
3. Inspect unstaged modifications via `functions.*_git_diff_unstaged` using the same repo path and adjust context lines as needed.
4. Stage the intended changes through `functions.*_git_add`, supplying the repo path and explicit file list.
5. Confirm the staged snapshot with `functions.*_git_diff_staged` to ensure only desired updates are staged.
6. Commit the staged work with `functions.*_git_commit`, providing the repo path and a descriptive message.
7. Optionally review recent history with `functions.*_git_log` when preparing checkpoints or summaries.
